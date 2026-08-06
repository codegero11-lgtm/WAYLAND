cmake_minimum_required(VERSION 3.22)
project(aracne_bringup)

find_package(ament_cmake REQUIRED)
find_package(launch REQUIRED)
find_package(launch_ros REQUIRED)
find_package(aracne_msgs REQUIRED)
find_package(aracne_leg_kinematics REQUIRED)
find_package(aracne_simulation REQUIRED)
find_package(aracne_teleop REQUIRED)

install(DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/teleop_bridge.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
