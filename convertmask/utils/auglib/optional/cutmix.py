'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-11-18 10:07:35
LastEditors: xiaoshuyui
LastEditTime: 2020-11-20 13:49:16
'''
import random

import cv2
import numpy as np
from skimage import io


def cutmix(img1, img2, factor: float = 0.5):
    assert (type(img1) is str
            or type(img1) is np.ndarray), 'type of input error'
    assert (type(img2) is str
            or type(img2) is np.ndarray), 'type of input error'

    if isinstance(img1, str):
        img1 = io.imread(img1)

    if isinstance(img2, str):
        img2 = io.imread(img2)

    imgShape1 = img1.shape
    img2 = cv2.resize(img2, (imgShape1[1], imgShape1[0]),
                      interpolation=cv2.INTER_CUBIC)

    startX = random.randint(0, int(0.5 * imgShape1[0]))
    startY = random.randint(0, int(0.5 * imgShape1[1]))

    rectHeight = random.randint(0, int(factor * imgShape1[0]))
    rectWidth = random.randint(0, int(factor * imgShape1[1]))

    img1[startX:startX + rectHeight, startY:startY + rectWidth] = 0
    img2[0:startX, :] = 0
    img2[startX + rectHeight:, :] = 0
    img2[:, 0:startY] = 0
    img2[:, startY + rectWidth:] = 0

    return img1 + img2
