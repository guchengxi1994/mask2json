'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-09-03 08:26:06
LastEditors: xiaoshuyui
LastEditTime: 2020-09-03 11:06:48
'''
import sys
sys.path.append("..")
import os

from convertmask.utils.xml2mask.x2m import *

save_dir = os.path.abspath(os.path.dirname(os.getcwd())) +os.sep + 'static'

if __name__ == "__main__":
    testList = ['aaa','dasd','1111']
    labels2yaml(testList,save_dir)