# AGV Mecanum Wheel Simulation System

A ROS 2 simulation system for an AGV (Automated Guided Vehicle) with mecanum wheels, featuring Gazebo Harmonic simulation, Nav2 navigation, and SLAM capabilities.

## Project Overview

This project provides a complete simulation environment for a four-wheeled mecanum AGV. It includes robot description (URDF/xacro), Gazebo simulation, Nav2-based autonomous navigation, and SLAM mapping.

## Features

- **Mecanum Wheel Kinematics**: Full holonomic motion control using mecanum wheels
- **Gazebo Harmonic Simulation**: Realistic physics simulation with ros2_control integration
- **Nav2 Integration**: Autonomous navigation with path planning and obstacle avoidance
- **SLAM Toolbox**: Simultaneous Localization and Mapping for map building
- **ros2_control**: Standardized hardware interface for robot control
- **Multi-package Architecture**: Modular design for easy extension

## Package Structure

```
src/
├── agv_mecanum_bringup/      # Top-level launch files
├── agv_mecanum_description/  # Robot URDF/xacro description
├── agv_mecanum_gazebo/       # Gazebo simulation worlds and launch
└── agv_mecanum_navigation/   # Nav2 and SLAM configuration
```

### Package Details

1. **agv_mecanum_description**
   - Robot URDF/xacro models with mecanum wheel geometry
   - ros2_control configuration for mecanum_drive_controller
   - Sensor integration (LiDAR, camera, IMU)

2. **agv_mecanum_gazebo**
   - Gazebo Harmonic simulation worlds
   - Bridge configuration for ROS 2 ↔ Gazebo communication
   - Controller spawning and configuration

3. **agv_mecanum_navigation**
   - Nav2 bringup with MPPI controller
   - SLAM Toolbox configuration for mapping
   - RViz2 visualization configurations

4. **agv_mecanum_bringup**
   - Complete system launch files
   - Teleoperation nodes
   - Integration of all components

## Dependencies

- ROS 2 (tested on Humble/Iron/Jazzy)
- Gazebo Harmonic
- Nav2 Stack
- SLAM Toolbox
- mecanum_drive_controller (from ros2_control)
- xacro
- robot_state_publisher
- rviz2

## Installation

### Prerequisites

Ensure you have ROS 2 and Gazebo Harmonic installed:

```bash
# Install ROS 2 (example for Ubuntu 22.04 - Humble)
sudo apt install ros-humble-desktop

# Install Gazebo Harmonic
sudo apt install gz-harmonic

# Install Nav2 and SLAM packages
sudo apt install ros-humble-nav2-bringup ros-humble-slam-toolbox
```

### Build the Workspace

```bash
cd /home/sy/ros2_ws
colcon build
source install/setup.bash
```

## Usage

### 1. Launch Full System (Simulation + Navigation)

```bash
ros2 launch agv_mecanum_bringup full_system.launch.py
```

This launches:
- Gazebo simulation with the AGV model
- Nav2 navigation stack
- RViz2 for visualization and goal setting

### 2. Launch Simulation Only (No Navigation)

```bash
ros2 launch agv_mecanum_bringup sim_only.launch.py
```

Starts only the Gazebo simulation without navigation. You can control the robot with teleop or publish to `/cmd_vel`.

### 3. Teleoperation

```bash
ros2 launch agv_mecanum_bringup teleop.launch.py
```

Enables keyboard teleoperation of the simulated AGV.

## Control Interface

The AGV accepts standard ROS 2 `geometry_msgs/Twist` messages on the `/cmd_vel` topic:

- **Linear X**: Forward/backward motion
- **Linear Y**: Strafe left/right (mecanum feature)
- **Angular Z**: Rotation

## Map Building with SLAM

1. Launch the full system
2. Open RViz2 and add the map topic
3. Use teleop or publish velocity commands to explore
4. The map will be built in real-time using SLAM Toolbox
5. Save the map with:

```bash
ros2 run nav2_map_server map_saver_cli -f ~/my_map
```

## Navigation

1. After launching `full_system.launch.py`, set a goal in RViz2 using the "2D Pose Estimate" and "2D Goal Pose" tools
2. The Nav2 stack will plan and execute a path to the goal
3. Monitor navigation in RViz2 with the planned path and costmaps

## Configuration

Configuration files can be found in each package's `config/` directory. Key parameters:

- **Controller**: MPPI controller tuned for mecanum kinematics
- **Planner**: Nav2 planner configuration
- **SLAM**: SLAM Toolbox parameters for mapping

## License

Apache-2.0 License

## Maintainer

- **sy** <sy@todo.todo>

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## Acknowledgments

- ROS 2 community for the excellent robotics framework
- Nav2 team for the navigation stack
- Gazebo team for the simulation environment