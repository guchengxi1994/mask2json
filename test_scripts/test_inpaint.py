'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-10-26 09:07:15
LastEditors: xiaoshuyui
LastEditTime: 2020-10-26 09:31:00
'''
import sys

sys.path.append("..")
import os

from convertmask.utils.auglib.optional.inpaint import rectangleInpaint,polygonInpaint

from skimage import io

if __name__ == "__main__":
    BASE_DIR = os.path.abspath(os.path.dirname(
        os.getcwd())) + os.sep + 'static'
    imgPath = BASE_DIR + os.sep + 'testInpaint.jpg'
    oriImg = io.imread(BASE_DIR + os.sep + 'multi_objs_test.jpg')

    inpaintImg = polygonInpaint(oriImg)
    # inpaintImg = rectangleInpaint(oriImg)
    io.imsave(imgPath, inpaintImg)
