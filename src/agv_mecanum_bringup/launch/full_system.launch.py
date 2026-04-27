import os
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_gazebo = get_package_share_directory('agv_mecanum_gazebo')
    pkg_nav = get_package_share_directory('agv_mecanum_navigation')

    default_map = os.path.join(pkg_nav, 'maps', 'warehouse_map.yaml')

    # 1. Gazebo simulation
    gazebo_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo, 'launch', 'gazebo.launch.py')
        ),
    )

    # 2. Navigation stack — pass map and use_slam through
    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav, 'launch', 'full_navigation.launch.py')
        ),
        launch_arguments={
            'map': LaunchConfiguration('map'),
            'use_slam': LaunchConfiguration('use_slam'),
        }.items(),
    )

    delayed_navigation = TimerAction(period=8.0, actions=[navigation])

    return LaunchDescription([
        DeclareLaunchArgument('map', default_value=default_map),
        DeclareLaunchArgument('use_slam', default_value='false'),
        gazebo_sim,
        delayed_navigation,
    ])
