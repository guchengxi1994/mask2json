'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-09-03 11:04:01
LastEditors: xiaoshuyui
LastEditTime: 2020-09-03 13:35:06
'''
import sys
sys.path.append("..")
import os

from convertmask.utils.xml2mask.x2m import *

save_dir = os.path.abspath(os.path.dirname(os.getcwd())) +os.sep + 'static'

if __name__ == "__main__":
    generateMask(save_dir+os.sep+'label_255.xml')
    print('########')
    label_masks,_ = x2mConvert(save_dir+os.sep+'label_255.xml')
    print(label_masks)

