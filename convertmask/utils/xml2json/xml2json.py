'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-09-24 09:03:04
LastEditors: xiaoshuyui
LastEditTime: 2020-09-24 09:32:24
'''
import xml.etree.ElementTree as ET 
from convertmask.utils.methods.img2base64 import imgEncode
from convertmask.utils.methods.logger import logger

def x2jConvert(xmlpath,originImgPath):
    # pass
    base64Code = imgEncode(originImgPath)


def getPolygon(xmlPath):
    in_file = open(xmlPath)
    tree = ET.parse(in_file)
    root = tree.getroot()
    
    for obj in root.iter('object'):
        pass