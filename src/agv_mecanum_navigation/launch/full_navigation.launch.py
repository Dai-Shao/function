import os
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    SetEnvironmentVariable,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.descriptions import ParameterFile
from nav2_common.launch import RewrittenYaml
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_nav = get_package_share_directory('agv_mecanum_navigation')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')

    params_file = os.path.join(pkg_nav, 'config', 'nav2.yaml')
    slam_params = os.path.join(pkg_nav, 'config', 'slam.yaml')
    rviz_config = os.path.join(pkg_nav, 'rviz', 'nav_config.rviz')
    default_map = os.path.join(pkg_nav, 'maps', 'warehouse_map.yaml')

    map_yaml = LaunchConfiguration('map', default=default_map)
    use_slam = LaunchConfiguration('use_slam', default='false')

    # Rewrite nav2.yaml: inject map path into yaml_filename
    configured_params = ParameterFile(
        RewrittenYaml(
            source_file=params_file,
            root_key='',
            param_rewrites={'yaml_filename': map_yaml},
            convert_types=True,
        ),
        allow_substs=True,
    )

    stdout_linebuf_envvar = SetEnvironmentVariable(
        'RCUTILS_LOGGING_BUFFERED_STREAM', '1'
    )

    # Condition: only when NOT using SLAM
    use_maploc = IfCondition(PythonExpression(['not ', use_slam]))

    # map_server — loads the pre-built map (only in map+AMCL mode)
    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[configured_params],
        condition=use_maploc,
    )

    # AMCL — localizes the robot using the pre-built map (only in map+AMCL mode)
    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[configured_params],
        condition=use_maploc,
    )

    # Lifecycle manager for map_server + AMCL (only in map+AMCL mode)
    lifecycle_localization = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[
            {'use_sim_time': True},
            {'autostart': True},
            {'node_names': ['map_server', 'amcl']},
        ],
        condition=use_maploc,
    )

    # Nav2 navigation stack (controller, planner, behavior, bt_navigator)
    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'navigation_launch.py')
        ),
        launch_arguments={
            'params_file': params_file,
            'use_sim_time': 'true',
        }.items(),
    )

    # SLAM Toolbox — alternative to AMCL when building map
    slam = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            slam_params,
            {'use_sim_time': True},
        ],
        condition=IfCondition(use_slam),
    )

    # RViz2
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        output='screen',
    )

    delayed_nav2 = TimerAction(period=2.0, actions=[nav2])
    delayed_rviz = TimerAction(period=3.0, actions=[rviz])

    return LaunchDescription([
        stdout_linebuf_envvar,
        DeclareLaunchArgument('map', default_value=default_map),
        DeclareLaunchArgument('use_slam', default_value='false'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),

        # Localization (map_server + AMCL + lifecycle manager)
        map_server,
        amcl,
        lifecycle_localization,
        # Nav2 stack
        delayed_nav2,
        # SLAM (alternative to AMCL)
        slam,
        delayed_rviz,
    ])
