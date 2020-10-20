'''
lanhuage: python
Descripttion: test convert label(file or list) to yaml file.
version: beta
Author: xiaoshuyui
Date: 2020-09-03 08:26:06
LastEditors: xiaoshuyui
LastEditTime: 2020-10-20 09:41:21
'''
import sys
sys.path.append("..")
import os

from convertmask.utils.xml2mask.x2m import *

save_dir = os.path.abspath(os.path.dirname(os.getcwd())) + os.sep + 'static'

if __name__ == "__main__":
    testList = ['aaa', 'dasd', '1111']
    labels2yaml(testList, save_dir)
