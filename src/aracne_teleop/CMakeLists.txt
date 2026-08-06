cmake_minimum_required(VERSION 3.22)
project(aracne_teleop)

find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(aracne_msgs REQUIRED)

install(PROGRAMS
  scripts/teleop_node.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
