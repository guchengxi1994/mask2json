'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-08-24 08:55:17
LastEditors: xiaoshuyui
LastEditTime: 2020-10-10 15:45:45
'''
try:
    import defusedxml.ElementTree as ET
except:
    import xml.etree.ElementTree as ET
# import pickle
import os
# from os import listdir, getcwd
# from os.path import join

xml_label_Dir = "xml"  # 需转换的xml路径
txt_label_Dir = 'txt/'  # 转换得的txt文件保存路径
classes = []
classes.append([
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O",
    "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"
])
classes = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]  #有几类就写几个

# classes.append("left")
# classes.append("right")
# classes.append("line_left")
# classes.append("line_right")
classes.append('IQI')
classes.append("CHINESEDATE")
classes.append("CROSS")
classes.append("ARROW")

print(classes)
# classes.append("cross_up_right")
# classes.append("cross_down_left")
# classes.append("cross_down_right")
# classes.append("cannotread")


def convert(size, box):  # 归一化操作
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)


if not os.path.exists(txt_label_Dir):
    os.makedirs(txt_label_Dir)
for rootDir, dirs, files in os.walk(xml_label_Dir):
    for file in files:
        file_name = file.split('.')[0]
        out_file = open(txt_label_Dir + '%s.txt' % (file_name), 'w')
        in_file = open("%s/%s" % (rootDir, file))
        tree = ET.parse(in_file)
        root = tree.getroot()
        size = root.find('size')
        w = int(size.find('width').text)
        h = int(size.find('height').text)

        for obj in root.iter('object'):
            difficult = obj.find('difficult').text
            cls = obj.find('name').text
            if cls not in classes or int(difficult) == 1:
                continue
            cls_id = classes.index(cls)
            xmlbox = obj.find('bndbox')
            b = (float(xmlbox.find('xmin').text),
                 float(xmlbox.find('xmax').text),
                 float(xmlbox.find('ymin').text),
                 float(xmlbox.find('ymax').text))
            bb = convert((w, h), b)
            out_file.write(
                str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')
        out_file.close()
