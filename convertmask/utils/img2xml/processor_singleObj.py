'''
@lanhuage: python
@Descripttion:  https://blog.csdn.net/qq_33196814/article/details/99992771
@version: beta
@Author: xiaoshuyui
@Date: 2020-04-22 17:07:28
LastEditors: xiaoshuyui
LastEditTime: 2020-10-10 15:42:02
'''
# import json
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


# if __name__ == "__main__":
#     # with open("D:\\getWeld\\insertXML\\test2.xml",'rb') as f:
#     f = open("D:\\getWeld\\insertXML\\test2.xml",'w')
#     f.writelines(img2xml("test","aa","asas\\aa.xx",12,23,"aaa",123,444,4523,664))
#     f.close()
