'''
lanhuage: python
Descripttion: https://blog.csdn.net/dcrmg/article/details/80273818
version: beta
Author: xiaoshuyui
Date: 2020-10-26 08:31:13
LastEditors: xiaoshuyui
LastEditTime: 2020-10-26 09:54:24
'''
import cv2
import numpy as np
import random


def persTrans(img: np.ndarray, factor=0.5):
    h, w = img.shape[:2]
    hRandom1 = random.randint(0, int(factor * h))
    wRandom1 = random.randint(0, int(factor * w))
    hRandom2 = random.randint(0, int(factor * h))
    wRandom2 = random.randint(0, int(factor * w))
    pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]])
    pts1 = np.float32([[0, 0], [w - wRandom1, h - hRandom1],
                       [w - wRandom2, h - hRandom2], [w - 1, 0]])

    M = cv2.getPerspectiveTransform(pts, pts1)
    dst = cv2.warpPerspective(img, M, (h + 100, w + 100))

    return dst
