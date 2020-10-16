'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-10-12 16:13:26
LastEditors: xiaoshuyui
LastEditTime: 2020-10-12 16:25:50
'''
import sys
sys.path.append('..')
import os
from convertmask.utils.yolo2xml.yolo2xml import *

BASE_DIR = os.path.abspath(os.path.dirname(
    os.getcwd())) + os.sep + 'static' + os.sep + 'yolo2xml' + os.sep

if __name__ == "__main__":
    txtpath = BASE_DIR + 'test.txt'
    imgpath = BASE_DIR + 'test.jpg'
    labelPath = BASE_DIR + 'voc.names'
    y2xConvert(txtPath=txtpath,imgPath=imgpath,labelPath=labelPath)
