cmake_minimum_required(VERSION 3.8)
project(agv_mecanum_gazebo)

find_package(ament_cmake REQUIRED)

install(DIRECTORY worlds config launch DESTINATION share/${PROJECT_NAME})
install(PROGRAMS scripts/tf_relay.py scripts/drive_demo.py scripts/cmd_vel_bridge.py scripts/mecanum_bridge.py scripts/cmd_vel_relay.py DESTINATION lib/${PROJECT_NAME})

ament_package()
