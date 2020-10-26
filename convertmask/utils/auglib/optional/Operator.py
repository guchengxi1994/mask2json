'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-10-26 10:34:55
LastEditors: xiaoshuyui
LastEditTime: 2020-10-26 11:33:57
'''
import random

from convertmask.utils.auglib.optional import (crop, distort, inpaint, mosaic,
                                               perspective, resize)
from convertmask.utils.methods.logger import logger


class CropOperator(object):
    def __init__(self,
                 img,
                 startPoint: tuple = None,
                 rect_or_poly: str = 'rect',
                 noise: bool = True,
                 convexHull: bool = False,
                 cropNumber: int = 1):
        self.img = img
        self.startPoint = startPoint
        self.rect_or_poly = rect_or_poly
        self.noise = noise
        self.convexHull = convexHull
        self.cropNumber = cropNumber

    def _getCroppedImg(self):
        if self.rect_or_poly == 'rect':
            return crop.multiRectanleCrop(self.img, self.cropNumber,
                                          self.noise)

        elif self.rect_or_poly == 'poly':
            return crop.multiPolygonCrop(self.img, self.cropNumber, self.noise,
                                         self.convexHull)


class DistortOperator(object):
    def __init__(self, img):
        self.img = img

    def _getDistortImg(self):
        return distort.imgDistort(self.img, flag=False)


class InpaintOperator(object):
    def __init__(self,
                 img,
                 rect_or_poly: str = 'rect',
                 startPoint: tuple = None):
        self.img = img
        self.rect_or_poly = rect_or_poly
        self.startPoint = startPoint

    def _getInpaintImg(self):
        if self.rect_or_poly == 'rect':
            return inpaint.rectangleInpaint(self.img, self.startPoint)

        elif self.rect_or_poly == 'poly':
            return inpaint.polygonInpaint(self.img, self.startPoint)


class MosiacOperator(object):
    def __init__(self,
                 img,
                 heightFactor: float = 0.5,
                 widthFactor: float = 0.5,
                 getXmls: bool = False,
                 xmls: list = [],
                 savePath: str = ''):
        logger.warning(
            'This script is not suitable for single image augumentation.')

        self.img = img
        self.heightFactor = heightFactor
        self.widthFactor = widthFactor
        self.getXmls = getXmls
        self.xmls = xmls
        self.savePath = savePath

    def _getMosiacImg(self):
        if not self.getXmls:
            if self.heightFactor == 0.5 and self.widthFactor == 0.5:
                self.heightFactor = random.uniform(0.3, 0.7)
                self.widthFactor = random.uniform(0.3, 0.7)

            if not isinstance(self.img, list):
                self.img = [self.img]

            return mosaic.mosiac_img(self.img, self.heightFactor,
                                     self.widthFactor)

        else:
            if not isinstance(self.img, list):
                self.img = [self.img]

            mosaic.mosiacScript(self.img, self.xmls, self.savePath, flag=True)


class PerspectiveOperator(object):
    def __init__(self, img, factor=0.5):
        self.img = img
        self.factor = factor

    def _getPerImg(self):
        return perspective.persTrans(self.img, self.factor)


class ResizeOperator(object):
    def __init__(self,
                 img,
                 heightFactor: float = 1.0,
                 widthFactor: float = 1.0,
                 getXmls: bool = False,
                 xmlpath: str = ''):
        self.img = img
        self.getXmls = getXmls
        self.heightFactor = heightFactor
        self.widthFactor = widthFactor
        self.xml = xmlpath

    def _getResizeImg(self):
        if not self.getXmls:
            return resize.resize_img(self.img, self.heightFactor,
                                     self.widthFactor)

        else:
            return resize.resizeScript(self.img, self.xml, self.heightFactor,
                                       self.widthFactor)
