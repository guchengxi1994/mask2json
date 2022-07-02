'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-10-22 11:10:47
LastEditors: xiaoshuyui
LastEditTime: 2020-10-22 11:19:05
'''
import sys

sys.path.append('..')
import os

from convertmask.utils.auglib.img_aug import aug_labelimg

BASE_DIR = os.path.abspath(os.path.dirname(os.getcwd())) + os.sep + 'static'

imgPath2 = BASE_DIR + os.sep + 'multi_objs.jpg'
labelPath2 = BASE_DIR + os.sep + 'multi_objs.xml'

if __name__ == "__main__":
    aug_labelimg(imgPath2,labelPath2)
