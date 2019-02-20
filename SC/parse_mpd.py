
# coding: utf-8

# In[1]:


import xml.etree.cElementTree as ET
from xml.etree.ElementTree import ElementTree,Element
import os
ET.register_namespace('',"urn:mpeg:dash:schema:mpd:2011") 

def read_xml(in_path):
    '''读取并解析xml文件
        in_path: xml路径
        return: ElementTree'''
    tree = ElementTree()
    tree.parse(in_path)
    return tree

def write_xml(tree, out_path):
    '''将xml文件写出
        tree: xml树
        out_path: 写出路径'''
    tree.write(out_path,encoding="utf-8",xml_declaration=True)

def if_match(node, kv_map):
    '''判断某个节点是否包含所有传入参数属性
        node: 节点
        kv_map: 属性及属性值组成的map'''
    for key in kv_map:
        if node.get(key) != kv_map.get(key):
            return False
    return True

#---------------search -----

def find_nodes(tree, path):
    '''查找某个路径匹配的所有节点
        tree: xml树
        path: 节点路径'''
    return tree.findall(path)


def get_node_by_keyvalue(nodelist, kv_map):
    '''根据属性及属性值定位符合的节点，返回节点
        nodelist: 节点列表
        kv_map: 匹配属性及属性值map'''
    i = 0
    result_nodes = []
    for node in nodelist:
        i=i+1
        if if_match(node, kv_map):
            #if (i == 2):
                result_nodes.append(node)
    return result_nodes

#---------------change -----

def change_node_properties(num, nodelist, kv_map, is_delete=False):
    '''修改/增加 /删除 节点的属性及属性值
        nodelist: 节点列表
        kv_map:属性及属性值map'''
    
    i = 0
    for node in nodelist:
        i=i+1
        for key in kv_map:
            if is_delete:
                if key in node.attrib:
                    del node.attrib[key]
            else:
                if (i==num):
                    node.set(key, kv_map.get(key))


def change_node_text(nodelist, text, is_add=False, is_delete=False):
    '''改变/增加/删除一个节点的文本
        nodelist:节点列表
        text : 更新后的文本'''
    for node in nodelist:
        if is_add:
            node.text += text
        elif is_delete:
            node.text = ""
        else:
            node.text = text

def create_node(tag, property_map, content):
    '''新造一个节点
        tag:节点标签
        property_map:属性及属性值map
        content: 节点闭合标签里的文本内容
        return 新节点'''
    element = Element(tag, property_map)
    element.text = content
    return element

def add_child_node(nodelist, element):
    '''给一个节点添加子节点
        nodelist: 节点列表
        element: 子节点'''
    for node in nodelist:
        
        node.append(element)

def del_node_by_tagkeyvalue(nodelist, tag, kv_map):
    '''同过属性及属性值定位一个节点，并删除之
        nodelist: 父节点列表
        tag:子节点标签
        kv_map: 属性及属性值列表'''
    for parent_node in nodelist:
        children = parent_node.getchildren()
        for child in children:
            if child.tag == tag and if_match(child, kv_map):
                parent_node.remove(child)


def get_tag_name(xml_element):
    """ Module to remove the xmlns tag from the name
        eg: '{urn:mpeg:dash:schema:mpd:2011}SegmentTemplate'
             Return: SegmentTemplate
    """
#     try:
    tag_name = xml_element[xml_element.find('}')+1:]
#     except TypeError:
#         config_dash.LOG.error("Unable to retrieve the tag. ")
#         return None
    return tag_name


# In[ ]:


from os import listdir
from os.path import isfile, join
#mypath="./"
#onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

onlyfiles=['dash_diving_10x10_qp28.mpd','dash_diving_10x10_qp32.mpd','dash_diving_10x10_qp36.mpd']
# In[5]:


for line in onlyfiles:
    if line == "parse_mpd.py":
        continue


# tree = read_xml('dash_coaster_10x10_qp32.mpd')
    tree = read_xml(line)
    root = tree.getroot()
    child_period = root[1];
    dir_path = "../../diving_m4s/"
#    dir_path = "../"+line.split("_")[1]+"/"
    # dir_path = "coaster_10x10/"

    i=0
    for adaptation_set in child_period:
        adaptation_set.remove(adaptation_set[0])
    #     print(adaptation_set[0])
        total_size=0.0
        if i==0:
            spec=adaptation_set[1][0].attrib['media'].split("_")
            for k in range(1,61):
                name = "_".join(spec[0:-1])+"_"+str(k)+".m4s"
#                print(name)
                
                if 'qp28' in name:
                    name=name.replace('qp28','qp36')
                elif 'qp32' in name:
                    name=name.replace('qp32','qp36')
#                print(name)
                file_size = os.path.getsize(dir_path+name)*8/1024.0
                total_size +=file_size
                new_ele = create_node("SegmentSize", {"id":name,"size":str(file_size), "scale":"Kbits"}, "")
                adaptation_set[1].append(new_ele)
                
        else:
            spec=adaptation_set[0][0].attrib['media'].split("_")
            for k in range(1,61):
                name = "_".join(spec[0:-1])+"_"+str(k)+".m4s"
                file_size = os.path.getsize(dir_path+name)*8/1024.0
                if file_size*1024 > 80000.0:
                    print(name)
                total_size +=file_size
                new_ele = create_node("SegmentSize", {"id":name,"size":str(file_size), "scale":"Kbits"}, "")
                adaptation_set[0].append(new_ele)       

        i=i+1
#    output = ""
#    for item in line.split("_")[:4]:
#        output=output+item
#    output += "_new.mpd"
    output = line[:-4]+"_new.mpd"
#    output = line.split("_")[:4]+"_new.mpd"   
    write_xml(tree, output)
    # write_xml(tree, "./dash_coaster_10x10_qp32_new.mpd")

