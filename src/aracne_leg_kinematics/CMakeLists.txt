cmake_minimum_required(VERSION 3.22)
project(aracne_leg_kinematics)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(aracne_msgs REQUIRED)
find_package(ament_cmake_gtest REQUIRED)

add_library(ik_solver STATIC
  src/ik_solver.cpp
)

target_include_directories(ik_solver PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
)

add_executable(leg_kinematics_node src/leg_kinematics_node.cpp)
target_include_directories(leg_kinematics_node PUBLIC include)
ament_target_dependencies(leg_kinematics_node
  rclcpp
  sensor_msgs
  std_msgs
  aracne_msgs
)
target_link_libraries(leg_kinematics_node ik_solver)

ament_add_gtest(test_ik_solver test/test_ik_solver.cpp)
if(TARGET test_ik_solver)
  target_link_libraries(test_ik_solver ik_solver)
endif()

install(TARGETS leg_kinematics_node
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY include/
  DESTINATION include/
)

ament_package()
