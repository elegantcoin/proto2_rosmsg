import re
import argparse
from pathlib import Path

# ROS -> Proto 类型映射
ros2proto_type_map = {
    "bool": "bool",
    "int8": "int32",
    "uint8": "uint32",
    "int16": "int32",
    "uint16": "uint32",
    "int32": "int32",
    "uint32": "uint32",
    "int64": "int64",
    "uint64": "uint64",
    "float32": "float",
    "float64": "double",
    "string": "string",
    "time": "int64",      # epoch time
    "duration": "int64",  # nanoseconds
}

proto2ros_type_map = {v: k for k, v in ros2proto_type_map.items()}


def rosmsg_to_proto(msg_file: Path, out_dir: Path):
    """单文件: ROS msg -> Proto"""
    lines = msg_file.read_text().splitlines()
    msg_name = msg_file.stem.capitalize()
    proto_lines = [f"message {msg_name} {{"]
    field_id = 1

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):  # 注释跳过
            continue

        m = re.match(r"(\w+)(\[\])?\s+(\w+)", line)
        if not m:
            continue

        ros_type, is_array, name = m.groups()
        proto_type = ros2proto_type_map.get(ros_type, ros_type)

        if is_array:
            proto_type = f"repeated {proto_type}"

        proto_lines.append(f"  {proto_type} {name} = {field_id};")
        field_id += 1

    proto_lines.append("}")

    out_file = out_dir / f"{msg_file.stem}.proto"
    out_file.write_text("\n".join(proto_lines))
    print(f"✅ {msg_file} -> {out_file}")


def proto_to_rosmsg(proto_file: Path, out_dir: Path):
    """单文件: Proto -> ROS msg"""
    lines = proto_file.read_text().splitlines()
    ros_lines = []

    for line in lines:
        line = line.strip()
        m = re.match(r"(repeated\s+)?(\w+)\s+(\w+)\s*=\s*\d+;", line)
        if not m:
            continue

        repeated, proto_type, name = m.groups()
        ros_type = proto2ros_type_map.get(proto_type, proto_type)

        if repeated:
            ros_type += "[]"

        ros_lines.append(f"{ros_type} {name}")

    out_file = out_dir / f"{proto_file.stem}.msg"
    out_file.write_text("\n".join(ros_lines))
    print(f"✅ {proto_file} -> {out_file}")


def batch_convert(src_dir: str, dst_dir: str, mode: str):
    """批量转换"""
    src_dir = Path(src_dir)
    dst_dir = Path(dst_dir)
    dst_dir.mkdir(parents=True, exist_ok=True)

    if mode == "ros2proto":
        for f in src_dir.glob("*.msg"):
            rosmsg_to_proto(f, dst_dir)
    elif mode == "proto2ros":
        for f in src_dir.glob("*.proto"):
            proto_to_rosmsg(f, dst_dir)
    else:
        raise ValueError("mode 必须是 ros2proto 或 proto2ros")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert between ROS .msg and Protobuf .proto definitions"
    )
    parser.add_argument("mode", choices=["ros2proto", "proto2ros"], help="转换模式")
    parser.add_argument("src", help="输入目录（包含 .msg 或 .proto 文件）")
    parser.add_argument("dst", help="输出目录")

    args = parser.parse_args()
    batch_convert(args.src, args.dst, args.mode)

