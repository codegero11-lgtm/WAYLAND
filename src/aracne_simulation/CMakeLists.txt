cmake_minimum_required(VERSION 3.22)
project(aracne_simulation)

find_package(ament_cmake REQUIRED)
find_package(xacro REQUIRED)

install(DIRECTORY worlds launch config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
