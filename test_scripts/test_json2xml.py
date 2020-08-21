'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-08-19 11:26:34
LastEditors: xiaoshuyui
LastEditTime: 2020-08-19 14:15:25
'''
import os
import sys
sys.path.append("..")
from convertmask.mask2json_utils.json2xml import j2xConvert

BASE_DIR = os.path.abspath(os.path.dirname(os.getcwd())) +os.sep + 'static'

j2xConvert(BASE_DIR+'/jsons_/multi_objs_rotation.json')

