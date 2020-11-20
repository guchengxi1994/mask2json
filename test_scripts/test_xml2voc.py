'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-11-19 16:53:28
LastEditors: xiaoshuyui
LastEditTime: 2020-11-19 17:07:27
'''
import glob
import os
import xml.etree.ElementTree as ET
from tqdm import tqdm


xmls = glob.glob('D:\\facedetect\\dump\\xmls_\\*.xml')
imgPath = '/home/aijr/face/efficient/imgs/'

classes = ['face']

with open('D:\\facedetect\\2007_voc.txt','w',encoding='utf-8') as f:
    for xml in tqdm(xmls):
        _,filename = os.path.split(xml)
        filename = filename.replace('.xml','.jpg')
        tree = ET.parse(xml)
        root = tree.getroot()
        for obj in root.iter('object'):
            difficult = 0 
            if obj.find('difficult')!=None:
                difficult = obj.find('difficult').text
                
            cls = obj.find('name').text
            if cls not in classes or int(difficult)==1:
                continue
            cls_id = classes.index(cls)
            xmlbox = obj.find('bndbox')
            b = (int(xmlbox.find('xmin').text), int(xmlbox.find('ymin').text), int(xmlbox.find('xmax').text), int(xmlbox.find('ymax').text))

            f.write(imgPath + filename+" " + ",".join([str(a) for a in b]) + ',' + str(cls_id)+'\n')