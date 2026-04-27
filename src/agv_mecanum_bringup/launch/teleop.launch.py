from launch import LaunchDescription
from launch.actions import ExecuteProcess


def generate_launch_description():
    # teleop_twist_keyboard requires a real terminal for keyboard input.
    # Launch it via xterm so it gets a proper tty.
    return LaunchDescription([
        ExecuteProcess(
            cmd=[
                'xterm', '-e',
                'ros2', 'run', 'teleop_twist_keyboard', 'teleop_twist_keyboard',
                '--ros-args',
                '-r', '/cmd_vel:=/mecanum_drive_controller/reference',
                '-p', 'stamped:=true',
            ],
            output='screen',
        ),
    ])
