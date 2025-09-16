#include <mcap/reader.hpp>
#include <rclcpp/rclcpp.hpp>
#include <rclcpp/serialization.hpp>

#include <geometry_msgs/msg/pose.hpp>
#include <nav_msgs/msg/odometry.hpp>

#include <iostream>
#include <memory>
#include <unordered_map>
#include <functional>

using DeserializeFn = std::function<void(const mcap::Message&)>;

template <typename T>
void deserialize_and_print(const mcap::Message& msg) {
  rclcpp::Serialization<T> serializer;
  T ros_msg;

  rclcpp::SerializedMessage serialized_msg;
  serialized_msg.reserve(msg.dataSize);
  serialized_msg.get_rcl_serialized_message().buffer_length = msg.dataSize;
  memcpy(serialized_msg.get_rcl_serialized_message().buffer, msg.data, msg.dataSize);

  serializer.deserialize_message(&serialized_msg, &ros_msg);

  // 简单打印几个字段（可以根据类型修改）
  if constexpr (std::is_same<T, geometry_msgs::msg::Pose>::value) {
    std::cout << "Pose: pos=("
              << ros_msg.position.x << ", "
              << ros_msg.position.y << ", "
              << ros_msg.position.z << ") "
              << "orient=("
              << ros_msg.orientation.x << ", "
              << ros_msg.orientation.y << ", "
              << ros_msg.orientation.z << ", "
              << ros_msg.orientation.w << ")" << std::endl;
  } else if constexpr (std::is_same<T, nav_msgs::msg::Odometry>::value) {
    std::cout << "Odometry: pos=("
              << ros_msg.pose.pose.position.x << ", "
              << ros_msg.pose.pose.position.y << ", "
              << ros_msg.pose.pose.position.z << ")" << std::endl;
  } else {
    std::cout << "反序列化成功，但没有专门的打印逻辑" << std::endl;
  }
}

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);

  if (argc < 4) {
    std::cerr << "用法: " << argv[0] << " <mcap_file> <topic_name> <msg_type>" << std::endl;
    std::cerr << "示例: " << argv[0] << " data.mcap /pose geometry_msgs/msg/Pose" << std::endl;
    return 1;
  }

  std::string filename = argv[1];
  std::string target_topic = argv[2];
  std::string msg_type = argv[3];

  // 注册支持的消息类型
  std::unordered_map<std::string, DeserializeFn> registry;
  registry["geometry_msgs/msg/Pose"] = &deserialize_and_print<geometry_msgs::msg::Pose>;
  registry["nav_msgs/msg/Odometry"] = &deserialize_and_print<nav_msgs::msg::Odometry>;

  if (registry.find(msg_type) == registry.end()) {
    std::cerr << "未支持的消息类型: " << msg_type << std::endl;
    return 1;
  }

  mcap::McapReader reader;
  auto status = reader.open(filename);
  if (!status.ok()) {
    std::cerr << "打开失败: " << status.message << std::endl;
    return 1;
  }

  size_t count = 0;
  for (auto it = reader.readMessages(); it != reader.readMessagesEnd(); ++it) {
    const mcap::Message& msg = *it;
    if (msg.channel->topic == target_topic) {
      registry[msg_type](msg);
      if (++count >= 5) break; // 只打印前5条
    }
  }

  reader.close();
  rclcpp::shutdown();
  return 0;
}

