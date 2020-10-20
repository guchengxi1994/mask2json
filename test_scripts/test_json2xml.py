'''
lanhuage: python
Descripttion: json to xml file test script.
version: beta
Author: xiaoshuyui
Date: 2020-08-19 11:26:34
LastEditors: xiaoshuyui
LastEditTime: 2020-10-20 09:40:51
'''
import os
import sys
sys.path.append("..")
from convertmask.utils.json2xml.json2xml import j2xConvert

BASE_DIR = os.path.abspath(os.path.dirname(os.getcwd())) + os.sep + 'static'

j2xConvert(BASE_DIR + '/jsons_/multi_objs_rotation.json')
