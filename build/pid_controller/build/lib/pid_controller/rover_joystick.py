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
        self.joystick_out1=Vector3()
        self.joystick_out2=Vector3()
        # Similarly create subscribers for pid_tuning_altitude, pid_tuning_roll, pid_tuning_pitch and any other subscriber if required
       
        self.pid_left = node.create_subscription(PidTune,"/lpid_params",self.pid_tune_left_callback,1)
        self.pid_right = node.create_subscription(PidTune, "/rpid_params", self.pid_tune_right_callback,1)
        self.joystick=node.create_subscription(Joy,"/joy",self.joystick_callback,1)

        # Create publisher for sending commands to differential drive

        self.pwm_pub1 = node.create_publisher(Vector3, "/pwm_output1",1)
        self.pwm_pub2 = node.create_publisher(Vector3, "/pwm_output2",1)


    
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
                self.joystick_out1.x=100.0
                self.joystick_out1.y=100.0
                self.joystick_out1.z=100.0
                self.joystick_out2.x=100.0
                self.joystick_out2.y=100.0
                self.joystick_out2.z=100.0
            elif(self.axes[4]<0 and self.axes[0]==0):
                self.joystick_out1.x=-100.0
                self.joystick_out1.y=-100.0
                self.joystick_out1.z=-100.0
                self.joystick_out2.x=-100.0
                self.joystick_out2.y=-100.0
                self.joystick_out2.z=-100.0
            elif(self.axes[0]>0 and self.axes[4]>0):
                self.joystick_out1.x=50.0
                self.joystick_out1.y=100.0
                self.joystick_out1.z=50.0
                self.joystick_out2.x=100.0
                self.joystick_out2.y=50.0
                self.joystick_out2.z=100.0
            elif(self.axes[0]<0 and self.axes[4]>0):
                self.joystick_out1.x=100.0
                self.joystick_out1.y=50.0
                self.joystick_out1.z=100.0
                self.joystick_out2.x=50.0
                self.joystick_out2.y=100.0
                self.joystick_out2.z=50.0
            elif(self.axes[0]>0 and self.axes[4]<0):
                self.joystick_out1.y=-100.0
                self.joystick_out1.x=-50.0
                self.joystick_out1.z=-100.0
                self.joystick_out2.y=-50.0
                self.joystick_out2.x=-100.0
                self.joystick_out2.z=-100.0
            elif(self.axes[0]<0 and self.axes[4]<0):
                self.joystick_out1.y=-50.0
                self.joystick_out1.x=-100.0
                self.joystick_out1.z=-50.0
                self.joystick_out2.y=-100.0
                self.joystick_out2.x=-50.0
                self.joystick_out2.z=-100.0    
            else:
                self.joystick_out1.y=0.0
                self.joystick_out1.x=0.0 
                self.joystick_out1.z=0.0
                self.joystick_out2.y=0.0
                self.joystick_out2.x=0.0
                self.joystick_out2.z=0.0       
        self.pwm_pub1.publish(self.joystick_out1)
        self.pwm_pub2.publish(self.joystick_out2)
        
        
           

def main(args=None):
    rclpy.init(args=args)

    node = rclpy.create_node('controller')
    node.get_logger().info(f"Node Started")
    #node.get_logger().info("Entering PID controller loop")

    controller = PIDController(node)
    while rclpy.ok():
        controller.joystick_control()
        rclpy.spin_once(node) # Sleep for 1/30 secs

    # except Exception as err:
    #     print(err)
    # # except:
    #     pass

    
    node.destroy_node()
    rclpy.shutdown()



if __name__ == '__main__':
    main()