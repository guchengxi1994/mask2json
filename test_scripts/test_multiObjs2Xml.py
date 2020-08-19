'''
@lanhuage: python
@Descripttion: 
@version: beta
@Author: xiaoshuyui
@Date: 2020-07-14 08:46:20
LastEditors: xiaoshuyui
LastEditTime: 2020-08-19 14:17:17
'''
import sys
sys.path.append("..")
import os
from utils.getMultiShapes import getMultiObjs_voc as gvoc

# BASE_DIR = os.path.abspath(os.curdir) +os.sep + 'static'
BASE_DIR = os.path.abspath(os.path.dirname(os.getcwd())) +os.sep + 'static'

imgPath = BASE_DIR + os.sep + 'multi_objs.jpg'
labelPath = BASE_DIR + os.sep + 'label_255.png'

savePath = BASE_DIR

gvoc(imgPath,labelPath,savePath)