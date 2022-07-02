'''
Descripttion: 
version: 
Author: xiaoshuyui
email: guchengxi1994@qq.com
Date: 2022-07-02 19:13:54
LastEditors: xiaoshuyui
LastEditTime: 2022-07-02 19:59:54
'''
import sys,os

sys.path.append('..')
BASE_DIR = os.path.abspath(os.path.dirname(os.getcwd())) + os.sep + 'static'

imgPath = BASE_DIR + os.sep + 'test702.jpg'
labelPath = BASE_DIR + os.sep + 'test702.json'
yamlPath = BASE_DIR + os.sep + 'test702.yaml'

from  convertmask.utils.json2mask.convert_with_label import *

processor(labelPath,yamlPath)