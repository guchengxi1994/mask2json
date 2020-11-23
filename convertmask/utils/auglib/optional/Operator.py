'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-10-26 10:34:55
LastEditors: xiaoshuyui
LastEditTime: 2020-11-10 11:29:03
'''
import random

import numpy as np
from convertmask.utils.auglib.optional import (crop, distort, inpaint, mosaic,
                                               perspective, resize)
from convertmask.utils.methods.logger import logger


class CropOperator(object):
    def __init__(self,
                 img=None,
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

    def setImgs(self, imgs):
        self.img = imgs

    def do(self):
        if self.img is not None:
            if isinstance(self.img, str) or isinstance(self.img, np.ndarray):
                if self.rect_or_poly == 'rect':
                    return crop.multiRectanleCrop(self.img, self.cropNumber,
                                                  self.noise)

                elif self.rect_or_poly == 'poly':
                    return crop.multiPolygonCrop(self.img, self.cropNumber,
                                                 self.noise, self.convexHull)
            else:
                res = []
                for i in self.img:
                    if self.rect_or_poly == 'rect':
                        res.append(
                            crop.multiRectanleCrop(i, self.cropNumber,
                                                   self.noise))

                    elif self.rect_or_poly == 'poly':
                        res.append(
                            crop.multiPolygonCrop(i, self.cropNumber,
                                                  self.noise, self.convexHull))

                return res
        else:
            logger.error('Images are not found!')


class DistortOperator(object):
    def __init__(self, img=None):
        self.img = img

    def setImgs(self, imgs):
        self.img = imgs

    def do(self):
        if self.img is not None:
            if isinstance(self.img, str) or isinstance(self.img, np.ndarray):
                return distort.imgDistort(self.img, flag=False)
            else:
                res = []
                for i in self.img:
                    res.append(distort.imgDistort(i, flag=False))
                return res
        else:
            logger.error('Images are not found!')


class InpaintOperator(object):
    def __init__(self,
                 img=None,
                 rect_or_poly: str = 'rect',
                 startPoint: tuple = None):
        self.img = img
        self.rect_or_poly = rect_or_poly
        self.startPoint = startPoint

    def setImgs(self, imgs):
        self.img = imgs

    def do(self):
        if self.img is not None:
            if isinstance(self.img, str) or isinstance(self.img, np.ndarray):
                if self.rect_or_poly == 'rect':
                    return inpaint.rectangleInpaint(self.img, self.startPoint)

                elif self.rect_or_poly == 'poly':
                    return inpaint.polygonInpaint(self.img, self.startPoint)
            else:
                res = []
                for i in self.img:
                    res.append(inpaint.polygonInpaint(i, self.startPoint))
                return res
        else:
            logger.error('Images are not found!')


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
    def __init__(self, img=None, factor=0.5):
        self.img = img
        self.factor = factor

    def setImgs(self, imgs):
        self.img = imgs

    def do(self):
        if self.img is not None:
            if isinstance(self.img, str) or isinstance(self.img, np.ndarray):
                return perspective.persTrans(self.img, self.factor)
            else:
                res = []
                for i in self.img:
                    res.append(perspective.persTrans(i, self.factor))
                return res
        else:
            logger.error('Images are not found!')


class ResizeOperator(object):
    def __init__(self,
                 img=None,
                 heightFactor: float = 1.0,
                 widthFactor: float = 1.0,
                 getXmls: bool = False,
                 xmlpath: str = ''):
        self.img = img
        self.getXmls = getXmls
        self.heightFactor = heightFactor
        self.widthFactor = widthFactor
        self.xml = xmlpath

    def setImgs(self, imgs):
        self.img = imgs

    def do(self):
        if self.img is not None:
            if not self.getXmls:
                if isinstance(self.img, str) or isinstance(
                        self.img, np.ndarray):
                    return resize.resize_img(self.img, self.heightFactor,
                                             self.widthFactor)
                else:
                    res = []
                    for i in self.img:
                        res.append(
                            resize.resize_img(i, self.heightFactor,
                                              self.widthFactor))
                    return res
            else:
                return resize.resizeScript(self.img, self.xml,
                                           self.heightFactor, self.widthFactor)
        else:
            logger.error('Images are not found!')
