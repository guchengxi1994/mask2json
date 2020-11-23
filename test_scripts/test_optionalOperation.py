'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-11-10 10:51:46
LastEditors: xiaoshuyui
LastEditTime: 2020-11-11 08:44:23
'''
import sys

sys.path.append("..")

import os
from convertmask.utils.auglib.optionsOperatorWithoutLabel import MainOptionalOperator 
from skimage import io


BASE_DIR = os.path.abspath(os.path.dirname(os.getcwd())) + os.sep + 'static'
imgPath = BASE_DIR + os.sep + 'multi_objs_test.jpg'

if __name__ == "__main__":
    m = MainOptionalOperator(imgPath)

    m._help()

    m.setCropAttributes(rect_or_poly='rect',noise=True,number=2)
    m.setDisortAttributes()
    m.setInpaintAttributes(rect_or_poly='poly')
    m.setPerspectiveAttributes(height=0.8,width=0.5,factor=0.8)
    m.setResizeAttributes(height=0.8,width=0.9)

    img = m.do()

    io.imsave(BASE_DIR + os.sep + '1110.jpg',img)

