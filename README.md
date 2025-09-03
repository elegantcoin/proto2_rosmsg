# proto2_rosmsg
convert proto file to rosmsg (cmake included)

![img](https://github.com/elegantcoin/proto2_rosmsg/blob/main/proto_msg_convetor_arch.png)


🚀 使用方法
##1. ROS msg → Proto

假设 msgs/ 目录下有多个 .msg 文件：

python ros_proto_converter.py ros2proto msgs protos


结果会生成到 protos/ 目录。

##2. Proto → ROS msg

python ros_proto_converter.py proto2ros protos msgs_out

📌 示例

输入 msgs/example.msg：

int32 id
string name
float64[] values


执行：

python ros_proto_converter.py ros2proto msgs protos


输出 protos/example.proto：

message Example {
  int32 id = 1;
  string name = 2;
  repeated double values = 3;
}


再执行：

python ros_proto_converter.py proto2ros protos msgs_out


输出 msgs_out/example.msg：

int32 id
string name
float64[] values
