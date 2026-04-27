cmake_minimum_required(VERSION 3.8)
project(agv_mecanum_navigation)

find_package(ament_cmake REQUIRED)

install(DIRECTORY config rviz maps launch DESTINATION share/${PROJECT_NAME})

ament_package()
