cmake_minimum_required(VERSION 3.8)
project(agv_mecanum_description)

find_package(ament_cmake REQUIRED)

install(DIRECTORY urdf config launch DESTINATION share/${PROJECT_NAME})

ament_package()
