'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-10-20 17:01:34
LastEditors: xiaoshuyui
LastEditTime: 2020-10-20 17:03:45
'''
import sys

sys.path.append('..')
import os

from convertmask.utils.json2mask.convertWithLabel import processor

BASE_DIR = os.path.abspath(os.path.dirname(os.getcwd())) + os.sep + 'static'
# print(BASE_DIR)
imgPath = BASE_DIR + os.sep + 'multi_objs.jpg'
labelPath = BASE_DIR + os.sep + 'multi_objs.json'

yamlFilePath = BASE_DIR + os.sep + 'multi_objs.yaml'

if __name__ == "__main__":
    processor(labelPath,yamlFilePath)
