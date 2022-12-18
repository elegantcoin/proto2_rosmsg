# print(import_map)
# print(len(mess_map))

def proto2msg_and_cmake(depends_ls,base,proto_name,mess_map):
    type_map ={"float":"float32","double":"float64"}
    for k,v in mess_map.items():
        # print(k,v)
        msg,tmp,tmp_enum,enum_name = "","","",""
        count,first_=0,0
        for line in v:
            if line[0]=="//" and count==0:
                msg+="# "+" ".join(line[1:])+"\n"
            elif line[0]=="enum":
                first_ = 1
                count+=1
                enum_name = line[1]
                tmp="# "+line[1]+" "
            elif line[0]=="}" or line[0]=="};":
                if first_==1:
                    msg+=tmp+"\n"
                    count-=1
                continue
            elif line[0]=="repeated":
                if "//" in line:
                    index = line.index("//")
                    msg+=" ".join(line[index:]).replace("//","#")+"\n"
                msg+=line[1]+"[] "+line[2]+"\n"
            elif count==0:
                if "//" in line:
                    index = line.index("//")
                    msg+=" ".join(line[index:]).replace("//","#")+"\n"
                if line[0] in ["float","double"]:
                    msg+=type_map.get(line[0],"error")+" "+line[1]+"\n"
                else:
                    msg+=line[0]+" "+line[1]+"\n"
            elif line[0]=="//" and count!=0:
                tmp +=" ".join(line)+" "
                tmp_enum +=" ".join(line)+" "
            else:
                tmp +="".join(line)+" "
                tmp_enum +="uint8 "+line[0]+"\n"
        # print(k)
        # print(msg)

        if not os.path.exists(base+proto_name):
            os.mkdir(base+proto_name)
            os.mkdir(base+proto_name+"/msg")
        with open(base+proto_name+"/msg/"+k+".msg", "w") as fw:
            fw.write(msg.strip())

    # cmake
    with open(base+proto_name+"/CMakeLists.txt", "w") as fw:
        msg_files="\n    ".join([i+".msg" for i in mess_map.keys()])
        content =f"cmake_minimum_required(VERSION 3.0.2)\nproject(de_{proto_name}_msgs)\n\nfind_package(catkin REQUIRED COMPONENTS message_generation std_msgs geometry_msgs)\n\nadd_message_files(\n    DIRECTORY msg\n    FILES\n    {msg_files}\n)\n\ngenerate_messages(DEPENDENCIES std_msgs geometry_msgs)\ncatkin_package(CATKIN_DEPENDS message_runtime std_msgs geometry_msgs)"
        fw.write(content)
    with open(base+proto_name+"/package.xml", "w") as fw:
        msg_build="\n".join(["  <build_depend>"+i+"</build_depend>" for i in depends_ls])
        msg_run="\n".join(["  <run_depend>"+i+"</run_depend>" for i in depends_ls])
        content =f"<package>\n  <name>de_{proto_name}_msgs</name>\n  <version>1.0.0</version>\n  <description>{proto_name} messages</description>\n  <maintainer email='XXXXXX@XXXXXX.com'>XXXXXX</maintainer>\n  <license>XXXXXXXXXXX</license>\n\n  <buildtool_depend>catkin</buildtool_depend>\n\n{msg_build}\n\n{msg_run}\n\n  <export>\n    <architecture_independent/>\n  </export>\n</package>\n"
        fw.write(content)

if __name__ == '__main__':
    proto_path = "proto/"
    proto_name = "map_speed_bump"

    output_base = "rosmsg/"

    depends_ls = ["message_runtime","std_msgs","de_time_msgs","de_geometry_msgs"]

    proto_name_list = ["map_speed_bump"]
    # proto_name_list = ["map_clear_area","map_crosswalk","map_geometry","map_id","map_junction","map_lane","map_overlap","map_parking_space","map_pnc_junction","map_road","map_rsu","map_signal","map_speed_bump","map_speed_control","map_stop_sign","map_yield_sign"]
    for proto_name in proto_name_list:
        mess_map = gen_msg_map(proto_path,proto_name)
        proto2msg_and_cmake(depends_ls,output_base,proto_name,mess_map)
