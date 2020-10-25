'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-10-23 17:14:44
LastEditors: xiaoshuyui
LastEditTime: 2020-10-23 17:53:53
'''
import sys

sys.path.append("..")
import os

from convertmask.utils.auglib.optional.crop import (multiPolygonCrop,
                                             multiRectanleCrop, polygonCrop,
                                             rectangleCrop)
from convertmask.utils.auglib.optional.generatePolygon import (generatePolygon,
                                                        generateRectangle)
from skimage import io

if __name__ == "__main__":
    # print('=========================')
    BASE_DIR = os.path.abspath(os.path.dirname(
        os.getcwd())) + os.sep + 'static'
    imgPath = BASE_DIR + os.sep + 'testCrop.jpg'
    oriImg = io.imread(BASE_DIR + os.sep + 'multi_objs_test.jpg')
    # mask = generatePolygon((500,500,3),convexHull=True)
    # mask2 = generateRectangle((500,500,3))
    # cropImg = rectangleCrop(oriImg, noise=True)
    # cropImg = polygonCrop(oriImg,noise=True)
    # cropImg = multiRectanleCrop(oriImg,number=3,noise=True)
    cropImg = multiPolygonCrop(oriImg,number=3,noise=True)
    io.imsave(imgPath, cropImg)
