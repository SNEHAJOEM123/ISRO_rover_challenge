#!/usr/bin/env python3

# standard imports
import copy
import time

# third-party imports
import scipy.signal
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.clock import Clock
from geometry_msgs.msg import Vector3
from pid_msg.msg import PidTune
from sensor_msgs.msg import Joy
# from swift_msgs.msg import PIDError, RCMessage
# from swift_msgs.srv import CommandBool



MIN_PWM1 = 0.0
BASE_PWM1 = 40.0
MAX_PWM1 = 255.0

MIN_PWM2 = 0.0
BASE_PWM2 = 80.0
MAX_PWM2 = 255.0



# Similarly, create upper and lower limits, base value, and max sum error values for roll and pitch

class PIDController():
    def __init__(self,node :Node):
        self.node= node
        self.set_point = 300        # Setpoints for x, y, z respectively      
        self.error = [0, 0]         # Error for roll, pitch and throttle        
        self.encoder_data=[0,0]
        self.axes=[]
        self.buttons=[]
        # Create variables for integral and differential error
        self.integral_error = [0, 0]
        self.derivative_error = [0, 0]

        # Create variables for previous error and sum_error
        self.prev_error = [0, 0]

        self.Kp = [ 72 * 0.00001  , 150 * 0.00001  ] #385 300 #260
 
        # Similarly create variables for Kd and Ki
        self.Ki = [ 90* 0.000002  , 38 * 0.000002] #300
        self.Kd = [ 1600 * 0.0001  , 900 * 0.0001] #1538 #1750

        self.encoder_out=Vector3()
        self.joystick_out=Vector3()
        # Similarly create subscribers for pid_tuning_altitude, pid_tuning_roll, pid_tuning_pitch and any other subscriber if required
       
        self.pid_left = node.create_subscription(PidTune,"/lpid_params",self.pid_tune_left_callback,1)
        self.pid_right = node.create_subscription(PidTune, "/rpid_params", self.pid_tune_right_callback,1)
        self.encoder=node.create_subscription(Vector3,"/encoder_data",self.encoder_data_callback,10)
        self.joystick=node.create_subscription(Joy,"/joy",self.joystick_callback,1)

        # Create publisher for sending commands to differential drive

        self.pid_pub = node.create_publisher(Vector3, "/pid_output",1)

    
    def pid_tune_left_callback(self, msg):
        self.Kp[0] = msg.kp * 0.01
        # self.Kp[2] = 480 *0.01
        self.Ki[0] = msg.ki * 0.0001
        self.Kd[0] = msg.kd * 0.1

    # Similarly add callbacks for other subscribers
    def pid_tune_right_callback(self, msg):
        self.Kp[1] = msg.kp * 0.01
        self.Ki[1] = msg.ki * 0.0001
        self.Kd[1] = msg.kd * 0.1


    def encoder_data_callback(self,msg):
        self.encoder_data[0]=msg.x
        self.encoder_data[1]=-msg.y
    
    def joystick_callback(self,msg):
        #print(msg.axes[0])
        self.axes=msg.axes
        self.buttons=msg.buttons
        print(self.axes)
        
        # self.buttons=msg.buttons


    def pid(self):          # PID algorithm
        print('in pid')
        # 0 : calculating Error, Derivative, Integral for Roll error : x axis
        try:
            self.error[0] = self.encoder_data[0] - self.set_point
        # Similarly calculate error for y and z axes 
            self.error[1] = self.encoder_data[1] - self.set_point

        except IndexError:
            pass
        # print(self.error)
        # Calculate derivative and intergral errors. Apply anti windup on integral error (You can use your own method for anti windup, an example is shown here)
        # for i in range(2):
            # self.integral_error[i] += self.error[i]
        self.derivative_error[0] = (self.error[0] - self.prev_error[0])
        self.derivative_error[1] = (self.error[1] - self.prev_error[1])
        # self.integral_error[2] += self.error[2]
        self.integral_error[0] += self.error[0]
        self.integral_error[1] += self.error[1]
        # self.integral[0] = (self.integral[0] + self.error[0])
        # if self.integral[0] > SUM_ERROR_ROLL_LIMIT:
        #     self.integral[0] = SUM_ERROR_ROLL_LIMIT
        # if self.integral[0] < -SUM_ERROR_ROLL_LIMIT:
        #     self.integral[0] = -SUM_ERROR_ROLL_LIMIT
        # Save current error in previous error
        self.prev_error[0] = self.error[0]
        self.prev_error[1] = self.error[1]

        # 1 : calculating Error, Derivative, Integral for Pitch error : y axis
        self.out_left = (self.Kp[0]*self.error[0]) + (self.Ki[0]*self.integral_error[0]) + (self.Kd[0]*self.derivative_error[0])
        self.out_right = (self.Kp[1]*self.error[1]) + (self.Ki[1]*self.integral_error[1]) + (self.Kd[1]*self.derivative_error[1])

        # 2 : calculating Error, Derivative, Integral for Alt error : z axis


        # Write the PID equations and calculate the self.rc_message.rc_throttle, self.rc_message.rc_roll, self.rc_message.rc_pitch
        self.encoder_out.x= float(BASE_PWM1 - round(self.out_left))
        self.encoder_out.y= float(BASE_PWM2 - round(self.out_right))

        if self.encoder_out.x>MAX_PWM1:
            self.encoder_out.x=MAX_PWM1
        
        if self.encoder_out.x<MIN_PWM1:
            self.encoder_out.x=MIN_PWM1

        if self.encoder_out.y>MAX_PWM1:
            self.encoder_out.y=MAX_PWM1
        
        if self.encoder_out.y<MIN_PWM1:
            self.encoder_out.y=MIN_PWM1
        self.joystick_control()
    #------------------------------------------------------------------------------------------------------------------------

    def joystick_control(self):
        if(self.axes!=[]):
            if(self.axes[4]>0 and self.axes[0]==0):
                self.joystick_out.x=self.encoder_out.x
                self.joystick_out.y=self.encoder_out.y
            elif(self.axes[4]<0 and self.axes[0]==0):
                self.joystick_out.x=-self.encoder_out.x
                self.joystick_out.y=-self.encoder_out.y
            elif(self.axes[0]>0 and self.axes[4]>0):
                self.joystick_out.x=(self.encoder_out.x)/2
                self.joystick_out.y=self.encoder_out.y
            elif(self.axes[0]<0 and self.axes[4]>0):
                self.joystick_out.y=(self.encoder_out.y)/2
                self.joystick_out.x=self.encoder_out.x
            elif(self.axes[0]>0 and self.axes[4]<0):
                self.joystick_out.y=-self.encoder_out.y
                self.joystick_out.x=(-self.encoder_out.x)/2
            elif(self.axes[0]<0 and self.axes[4]<0):
                self.joystick_out.y=(-self.encoder_out.y)/2
                self.joystick_out.x=-self.encoder_out.x
            else:
                self.joystick_out.y=0.0
                self.joystick_out.x=0.0        
        self.pid_pub.publish(self.joystick_out)
        
        
           

def main(args=None):
    rclpy.init(args=args)

    node = rclpy.create_node('controller')
    node.get_logger().info(f"Node Started")
    node.get_logger().info("Entering PID controller loop")

    controller = PIDController(node)
    while rclpy.ok():
        controller.pid()
        rclpy.spin_once(node) # Sleep for 1/30 secs

    # except Exception as err:
    #     print(err)
    # # except:
    #     pass

    
    node.destroy_node()
    rclpy.shutdown()



if __name__ == '__main__':
    main()