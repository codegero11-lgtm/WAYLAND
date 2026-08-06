cmake_minimum_required(VERSION 3.22)
project(aracne_msgs)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/LegTarget.msg"
  "msg/TeleopCmd.msg"
  "srv/ComputeIK.srv"
)

ament_package()
