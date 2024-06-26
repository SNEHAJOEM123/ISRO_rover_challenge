from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='pid_tune',
            executable='pid_tune_drone.py',
            name='tune_pid_drone',
            parameters=[
                {'ppid_ui_enable': True},
                {'rpid_ui_enable': True},
                {'ypid_ui_enable': False},
                {'tpid_ui_enable': True},
            ],
        ),
    ])
