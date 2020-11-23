'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-10-26 09:36:20
LastEditors: xiaoshuyui
LastEditTime: 2020-10-26 09:58:50
'''
import sys

sys.path.append("..")
import os
from skimage import io
from convertmask.utils.auglib.optional.perspective import persTrans


if __name__ == "__main__":
    BASE_DIR = os.path.abspath(os.path.dirname(
        os.getcwd())) + os.sep + 'static'
    imgPath = BASE_DIR + os.sep + 'testPers.jpg'
    oriImg = io.imread(BASE_DIR + os.sep + 'multi_objs_test.jpg')

    perImg = persTrans(oriImg,0.2)
    # inpaintImg = rectangleInpaint(oriImg)
    io.imsave(imgPath, perImg)