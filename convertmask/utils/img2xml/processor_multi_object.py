'''
lanhuage: python
Descripttion:  https://blog.csdn.net/qq_33196814/article/details/99992771
version: beta
Author: xiaoshuyui
Date: 2020-04-22 17:07:28
LastEditors: xiaoshuyui
LastEditTime: 2021-02-19 16:50:40
'''
import os
try:
    import defusedxml.ElementTree as ET
except:
    import xml.etree.ElementTree as ET
from xml.dom.minidom import parse

import xmltodict


def json_to_xml(json_str):
    # xmltodict库的unparse()json转xml
    # 参数pretty 是格式化xml
    xml_str = xmltodict.unparse(json_str, pretty=1)
    return xml_str


def root2annotion(xml_str):
    pass


def img2xml(folder:str,filename:str,path:str,width:int,height:int,name:str, \
    xmin:int,ymin:int,xmax:int,ymax:int):

    annotation = {}
    # annotation['folder'] = "HBXZ"
    annotation['folder'] = folder
    annotation['filename'] = filename
    # annotation['filename'] = "xxx.jpg"
    annotation['path'] = path
    # annotation['path'] = "xxxx\\xxxxx\\xxx.jpg"

    source = {}
    source['database'] = "Unknown"

    annotation['source'] = source

    size = {}
    size['width'] = width
    # size['width'] = 903
    # size['height'] = 1722
    size['height'] = height
    size['depth'] = 1

    annotation['size'] = size

    annotation['segmented'] = 0

    # object = {}
    ob = {}
    ob['name'] = name
    ob['difficult'] = 0
    # ob['name'] = 'weld'

    bndbox = {}
    # bndbox['xmin'] = 387
    # bndbox['ymin'] = 34
    # bndbox['xmax'] = 578
    # bndbox['ymax'] = 1622

    bndbox['xmin'] = xmin
    bndbox['ymin'] = ymin
    bndbox['xmax'] = xmax
    bndbox['ymax'] = ymax

    ob['bndbox'] = bndbox

    annotation['object'] = ob
    # dic = {}
    dicts = {'annotation': annotation}

    return json_to_xml(dicts)


def writeXML(domTree_path, aimPath, name: str, bndbox: dict):
    if os.path.exists(domTree_path):
        domTree = parse(domTree_path)
        # print(domTree)
        rootNode = domTree.documentElement
        # print(rootNode.nodeName)
        # print("<==================>reverse")
        # print(rootNode)
        customer_node = domTree.createElement("object")

        name_node = domTree.createElement("name")
        name_text_value = domTree.createTextNode(name)
        name_node.appendChild(name_text_value)  # 把文本节点挂到name_node节点
        customer_node.appendChild(name_node)

        phone_node = domTree.createElement("difficult")
        phone_text_value = domTree.createTextNode(str(0))
        phone_node.appendChild(phone_text_value)  # 把文本节点挂到name_node节点
        customer_node.appendChild(phone_node)

        comments_node = domTree.createElement("bndbox")
        xmin = domTree.createElement('xmin')
        ymin = domTree.createElement('ymin')
        xmax = domTree.createElement('xmax')
        ymax = domTree.createElement('ymax')
        # root = {}
        # root['bndbox'] = bndbox
        # s = '<?xml version="1.0" encoding="utf-8"?>'
        xmin_text = domTree.createTextNode(str(bndbox['xmin']))
        ymin_text = domTree.createTextNode(str(bndbox['ymin']))
        xmax_text = domTree.createTextNode(str(bndbox['xmax']))
        ymax_text = domTree.createTextNode(str(bndbox['ymax']))

        xmin.appendChild(xmin_text)
        ymin.appendChild(ymin_text)
        xmax.appendChild(xmax_text)
        ymax.appendChild(ymax_text)

        comments_node.appendChild(xmin)
        comments_node.appendChild(ymin)
        comments_node.appendChild(xmax)
        comments_node.appendChild(ymax)
        customer_node.appendChild(comments_node)

        rootNode.appendChild(customer_node)
        # print(rootNode.nodeName)
        # print(type(domTree))
        # domTree.writexml(domTree_path)
        with open(aimPath, 'w') as f:
            domTree.writexml(f, addindent='  ', encoding='utf-8')


def prettyXml(element,
              indent,
              newline,
              level=0):  # elemnt为传进来的Elment类，参数indent用于缩进，newline用于换行
    if element:  # 判断element是否有子元素
        if element.text == None or element.text.isspace(
        ):  # 如果element的text没有内容
            element.text = newline + indent * (level + 1)
        else:
            element.text = newline + indent * (level + 1) + element.text.strip(
            ) + newline + indent * (level + 1)
    #else:  # 此处两行如果把注释去掉，Element的text也会另起一行
    #element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * level
    temp = list(element)  # 将elemnt转成list
    for subelement in temp:
        if temp.index(subelement) < (
                len(temp) - 1):  # 如果不是list的最后一个元素，说明下一个行是同级别元素的起始，缩进应一致
            subelement.tail = newline + indent * (level + 1)
        else:  # 如果是list的最后一个元素， 说明下一行是母元素的结束，缩进应该少一个
            subelement.tail = newline + indent * level
        prettyXml(subelement, indent, newline, level=level + 1)  # 对子元素进行递归操作
    return element


def img2xml_multiobj(tmpPath: str, aimPath: str, folder: str, filename: str,
                     path: str, width: int, height: int, objs: list):
    """
    objs:list --> dict
    [{'name':'xxx','difficult':0,'bndbox':{'xmin':??,...,'ymax':???}}]

    """
    annotation = {}
    annotation['folder'] = folder
    annotation['filename'] = filename
    annotation['path'] = path

    source = {}
    source['database'] = "Unknown"

    annotation['source'] = source

    size = {}
    size['width'] = width
    size['height'] = height
    size['depth'] = 1

    annotation['size'] = size

    annotation['segmented'] = 0

    if len(objs) > 0:
        obj = objs[0]
        # print(obj)
        bnBox = obj['bndbox']

        f = open(tmpPath, 'w')
        f.writelines(img2xml(folder,filename,path,width,height, \
            obj['name'],bnBox['xmin'],bnBox['ymin'],bnBox['xmax'],bnBox['ymax']))
        f.close()

        if len(objs) > 1:
            # for i in objs:
            for i in range(1, len(objs)):
                o = objs[i]
                bn = o['bndbox']
                bndbox = {}

                bndbox['xmin'] = bn['xmin']
                bndbox['ymin'] = bn['ymin']
                bndbox['xmax'] = bn['xmax']
                bndbox['ymax'] = bn['ymax']

                writeXML(tmpPath, aimPath, o['name'], bndbox)

        domTree = ET.parse(tmpPath)
        root = domTree.getroot()
        root = prettyXml(root, '\t', '\n')
        tree = ET.ElementTree(root)
        tree.write(tmpPath)
