'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-11-12 09:35:13
LastEditors: xiaoshuyui
LastEditTime: 2020-11-12 10:52:18
'''
import sys

sys.path.append("..")

import os
from convertmask.utils.auglib.operator_without_label import MainOperatorWithoutLabel
from skimage import io

BASE_DIR = os.path.abspath(os.path.dirname(os.getcwd())) + os.sep + 'static'
imgPath = BASE_DIR + os.sep + 'multi_objs_test.jpg'

if __name__ == "__main__":
    m = MainOperatorWithoutLabel(imgPath)

    m._help()

    m.setZoomAttributes(size=0.8)
    m.setNoiseAttributes(noiseType=['gaussian', 'poisson', 's&p'])
    m.setRotationOperator(angle=25,scale=1.0)
    m.setTranslationOperation(th=100,tv=100)
    m.setFlip()

    m.setCropAttributes(rect_or_poly='rect',noise=True,number=2)
    m.setDisortAttributes()
    m.setInpaintAttributes(rect_or_poly='poly')
    m.setPerspectiveAttributes(height=0.8,width=0.5,factor=0.8)
    m.setResizeAttributes(height=0.8,width=0.9)

    img = m.do()

    for i in img:
        io.imsave(BASE_DIR + os.sep + '1112.jpg',i)