'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-10-26 08:31:13
LastEditors: xiaoshuyui
LastEditTime: 2020-11-12 10:30:05
'''
import cv2
import numpy as np
import skimage
from convertmask.utils.auglib.optional.generatePolygon import (
    generatePolygon, generateRectangle)
from convertmask.utils.methods.logger import logger


def rectangleInpaint(img:np.ndarray,startPoint:tuple=None):
    if isinstance(img,str):
        img = skimage.io.imread(img)
    imgShape = img.shape
    mask = generateRectangle(imgShape, startPoint)
    if len(mask.shape) == 3:
        mask = mask[:,:,0]
        
    dst_TELEA = cv2.inpaint(img,mask.astype(np.uint8),3,cv2.INPAINT_TELEA)
    return dst_TELEA


def polygonInpaint(img:np.ndarray,startPoint:tuple=None):
    if isinstance(img,str):
        img = skimage.io.imread(img)
    imgShape = img.shape
    mask = generatePolygon(imgShape, startPoint)
    if len(mask.shape) == 3:
        mask = mask[:,:,0]

    dst_TELEA = cv2.inpaint(img,mask.astype(np.uint8),3,cv2.INPAINT_TELEA)
    return dst_TELEA
