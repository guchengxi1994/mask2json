'''
lanhuage: python
Descripttion: test xmls to json files. currently is just supported for labelImg and labelImgTool (https://github.com/lzx1413/LabelImgTool)
version: beta
Author: xiaoshuyui
Date: 2020-09-24 09:41:23
LastEditors: xiaoshuyui
LastEditTime: 2020-10-20 09:49:30
'''
import sys

sys.path.append('..')
import os

from convertmask.utils.xml2json.xml2json import (getPolygon, x2jConvert,
                                                 x2jConvert_pascal)

BASE_DIR = os.path.abspath(os.path.dirname(os.getcwd())) + os.sep + 'static'

if __name__ == "__main__":
    # getPolygon(BASE_DIR+os.sep+'bbox_label.xml')
    x2jConvert(BASE_DIR + os.sep + 'bbox_label.xml',
               BASE_DIR + os.sep + 'bbox_label.jpg')

    x2jConvert_pascal(BASE_DIR + os.sep + 'bbox_label.xml',
                      BASE_DIR + os.sep + 'bbox_label.jpg')
