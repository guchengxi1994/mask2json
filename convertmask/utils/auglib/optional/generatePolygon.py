'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-10-23 17:01:06
LastEditors: xiaoshuyui
LastEditTime: 2020-10-23 17:54:20
'''
import random

import cv2
import numpy as np


def getHull(mask):
    if cv2.__version__.startswith('4.'):
        contours, _ = cv2.findContours(mask, cv2.RETR_LIST,
                                       cv2.CHAIN_APPROX_SIMPLE)
    else:
        _, contours, _ = cv2.findContours(mask, cv2.RETR_LIST,
                                          cv2.CHAIN_APPROX_SIMPLE)
    hull = []
    for i in range(len(contours)):
        hull.append(cv2.convexHull(contours[i], False))

    return hull


def generatePolygon(imgshape: tuple,
                    startpoint: tuple = None,
                    convexHull=False):
    points = random.randint(4, 10)
    # print(points)
    mask = np.zeros((imgshape))

    if startpoint is None:
        startX = random.randint(0, int(0.5 * imgshape[0]))
        startY = random.randint(0, int(0.5 * imgshape[1]))
    else:
        startX = startpoint[0] if startpoint[0] < 0.5 * imgshape[0] else int(
            0.5 * imgshape[0])
        startY = startpoint[1] if startpoint[1] < 0.5 * imgshape[1] else int(
            0.5 * imgshape[1])

    x_cor = np.random.randint(startX, imgshape[0], points).tolist()
    y_cor = np.random.randint(startY, imgshape[1], points).tolist()
    cor_xy = np.array(np.vstack((x_cor, y_cor)).T.tolist())

    if len(imgshape) == 3:
        cv2.fillPoly(mask, [cor_xy], (255, 255, 255))
    else:
        cv2.fillPoly(mask, [cor_xy], 255)

    if len(imgshape) == 3:
        mask = mask[:, :, 0]
    mask = mask.astype(np.uint8)
    if convexHull:
        hull = getHull(mask)
        cv2.fillPoly(mask, hull, 255)

    return mask.astype(np.uint8)


def generateRectangle(imgshape: tuple, startpoint: tuple = None):
    mask = np.zeros((imgshape))

    if startpoint is None:
        startX = random.randint(0, int(0.5 * imgshape[0]))
        startY = random.randint(0, int(0.5 * imgshape[1]))
    else:
        startX = startpoint[0] if startpoint[0] < 0.5 * imgshape[0] else int(
            0.5 * imgshape[0])
        startY = startpoint[1] if startpoint[1] < 0.5 * imgshape[1] else int(
            0.5 * imgshape[1])
    
    rectHeight = random.randint(0, int(0.5 * imgshape[0]))
    rectWidth = random.randint(0, int(0.5 * imgshape[1]))

    mask[startX:startX+rectHeight,startY:startY+rectWidth] = 255

    return mask.astype(np.uint8)
