'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-09-24 09:41:23
LastEditors: xiaoshuyui
LastEditTime: 2020-09-24 10:26:06
'''
import sys
sys.path.append('..')
import os

from convertmask.utils.xml2json.xml2json import getPolygon,x2jConvert
BASE_DIR = os.path.abspath(os.path.dirname(os.getcwd())) +os.sep + 'static'


if __name__ == "__main__":
    # getPolygon(BASE_DIR+os.sep+'bbox_label.xml')
    x2jConvert(BASE_DIR+os.sep+'bbox_label.xml',BASE_DIR+os.sep+'bbox_label.jpg')