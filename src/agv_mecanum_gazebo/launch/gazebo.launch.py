import os
from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    SetEnvironmentVariable,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_description = get_package_share_directory('agv_mecanum_description')
    pkg_gazebo = get_package_share_directory('agv_mecanum_gazebo')

    world_path = os.path.join(pkg_gazebo, 'worlds', 'warehouse.world')
    urdf_path = os.path.join(pkg_description, 'urdf', 'agv_mecanum.urdf.xacro')

    # Process xacro
    robot_description = ParameterValue(
        Command(['xacro ', urdf_path, ' use_gazebo:=true']),
        value_type=str
    )

    # 1. Gazebo Harmonic (server + client GUI)
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch', 'gz_sim.launch.py'
            )
        ),
        launch_arguments={
            'gz_args': ['-r ', world_path],
            'on_exit_shutdown': 'true',
        }.items(),
    )

    # 2. Robot State Publisher — remap /joint_states to Gazebo's joint state topic
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True,
        }],
        remappings=[
            ('/joint_states', '/world/warehouse/model/agv_mecanum/joint_state'),
        ],
    )

    # 3. Spawn robot in Gazebo
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'agv_mecanum',
            '-topic', 'robot_description',
            '-x', '0',
            '-y', '0',
            '-z', '0.05',
        ],
        output='screen',
    )

    # 4. Sensor bridges (Gazebo → ROS)
    bridge_clock = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen',
    )

    bridge_scan = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan'],
        output='screen',
    )

    bridge_imu = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/imu@sensor_msgs/msg/Imu[gz.msgs.IMU'],
        output='screen',
    )

    # 5. Joint state bridge — Gazebo joint states → ROS for RViz
    # Gazebo publishes to /world/warehouse/model/agv_mecanum/joint_state
    # Bridge it to ROS with the same topic name
    bridge_joint_states = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/world/warehouse/model/agv_mecanum/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model'],
        output='screen',
    )

    # 6. Mecanum drive bridges (ROS ↔ Gazebo)
    # Gazebo mecanum plugin subscribes to /model/agv_mecanum/cmd_vel
    bridge_cmd_vel = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/model/agv_mecanum/cmd_vel@geometry_msgs/msg/Twist[gz.msgs.Twist'],
        output='screen',
    )

    # Gazebo odometry → ROS /odom
    bridge_odom = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/model/agv_mecanum/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry'],
        output='screen',
    )

    # Gazebo TF → ROS /tf (mecanum plugin publishes to /tf in Gazebo)
    bridge_tf = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V'],
        output='screen',
    )

    # 7. cmd_vel relay: Nav2 /cmd_vel → Gazebo mecanum /model/agv_mecanum/cmd_vel
    cmd_vel_relay = Node(
        package='agv_mecanum_gazebo',
        executable='cmd_vel_relay.py',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    # Delayed startup: wait for Gazebo to initialize
    delayed_bridges = TimerAction(
        period=10.0,
        actions=[
            bridge_cmd_vel,
            bridge_odom,
            bridge_tf,
            bridge_joint_states,
            cmd_vel_relay,
        ],
    )

    return LaunchDescription([
        # Force Intel iris Mesa driver for Ogre2 rendering
        SetEnvironmentVariable('MESA_LOADER_DRIVER_OVERRIDE', 'iris'),
        SetEnvironmentVariable('LIBGL_DRI3_DISABLE', '1'),
        gz_sim,
        robot_state_publisher,
        spawn_robot,
        bridge_clock,
        bridge_scan,
        bridge_imu,
        delayed_bridges,
    ])
