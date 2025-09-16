cmake_minimum_required(VERSION 3.14)
project(mcap_ros2_dynamic_reader)

set(CMAKE_CXX_STANDARD 17)

find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)

# 假设 mcap 库在本地
add_subdirectory(mcap)

add_executable(mcap_ros2_dynamic_reader mcap_ros2_dynamic_reader.cpp)
ament_target_dependencies(mcap_ros2_dynamic_reader rclcpp geometry_msgs nav_msgs)
target_link_libraries(mcap_ros2_dynamic_reader PRIVATE mcap)

