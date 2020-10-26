'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-09-03 11:31:50
LastEditors: xiaoshuyui
LastEditTime: 2020-10-10 15:43:15
'''

import math

import cv2
import numpy as np
from skimage import io


def reshape_dengbili(img, imgname=None, bias=648):
    flag = False

    imgsize = img.shape
    x = imgsize[0]
    y = imgsize[1]
    #获取图像大小，如果图像x轴方向大于y轴方向，则旋转90度
    if x > y:
        img = cv2.flip(cv2.transpose(img), 1)
        flag = True

    else:
        pass

    imgsize = img.shape

    x = imgsize[0]
    y = imgsize[1]

    times = x / bias

    img = cv2.resize(img, (int(y / times), bias))

    dim_x = 0
    tmp = math.ceil(y / 1000) * 1000
    tmp1 = math.ceil(y / 1000 - 1) * 1000
    ymax = tmp if tmp - tmp1 else tmp1
    dim_y = ymax - y if y < ymax else 0

    img = cv2.copyMakeBorder(img, 0, dim_x, 0, dim_y, cv2.BORDER_ISOLATED)

    img = np.array(img[:, 0:ymax], np.uint8)
    del tmp, tmp1
    return img


def splitImg_dengbili(img, imgName='', bias=1000, savePath='', savefile=True):
    imgList = []
    imgShape = img.shape
    times = int(imgShape[1] / bias)
    for i in range(0, times):
        img1 = img[:, i * bias:(i + 1) * bias]
        imgList.append(img1)
        if savefile:
            io.imsave(savePath + '_%s_%s.jpg' % (imgName, str(i)), img1)

    return imgList
