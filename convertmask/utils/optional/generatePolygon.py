'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-10-23 17:01:06
LastEditors: xiaoshuyui
LastEditTime: 2020-10-23 17:54:20
'''
import numpy as np
import random
import cv2
from convertmask.utils.methods.getShape import get_approx as getHull


# def getHull(mask):
#     img_bin, contours, hierarchy = cv2.findContours(mask, cv2.RETR_LIST,
#                                                     cv2.CHAIN_APPROX_SIMPLE)
#     # img_adp = mask.copy()
#     epsilon = 0.02 * cv2.arcLength(contours[0], True)
#     approx = cv2.approxPolyDP(contours[0], epsilon, True)
#     return approx


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
    # print(x_cor)
    cor_xy = np.array(np.vstack((x_cor, y_cor)).T.tolist())

    # print(type(cor_xy))
    if len(imgshape) == 3:
        cv2.fillPoly(mask, [cor_xy], (255, 255, 255))
    else:
        cv2.fillPoly(mask, [cor_xy], 255)
    
    # print(mask.shape)
    if len(imgshape) == 3:
        mask = mask[:,:,0]
    mask = mask.astype(np.uint8)
    if convexHull:
        # pass
        img_bin, contours, hierarchy = cv2.findContours(mask, cv2.RETR_LIST,
                                                    cv2.CHAIN_APPROX_SIMPLE)
        region = getHull(mask,contours[0],0.1)
        cv2.fillPoly(mask, [region], 255)

    return mask.astype(np.uint8)


def generateRectangle(imgshape: tuple, startpoint: tuple = None):
    pass