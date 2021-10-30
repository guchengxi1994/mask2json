'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-11-11 08:34:07
LastEditors: xiaoshuyui
LastEditTime: 2020-11-12 10:50:59
'''
import gc
import os

import numpy as np
from convertmask.utils.auglib.img_aug_nolabel import (imgFlip, imgNoise,
                                                     imgRotation,
                                                     imgTranslation, imgZoom)
from convertmask.utils.auglib.options_operator_without_label import \
    MainOptionalOperator as OptionalOperator
from convertmask.utils.methods.logger import logger
from skimage import io


class ZoomOperator(object):
    def __init__(self, img=None, size: float = 1.0) -> None:
        self.img = img
        self.size = size

    def setImgs(self, imgs):
        self.img = imgs

    def setRandomSize(self, val: bool):
        assert type(
            val
        ) is bool, 'Input of {}.setRandomSize() MUST be a bool value'.format(
            self.__class__)
        if val:
            self.size = 1.0

    def do(self):
        if self.img is not None:
            if isinstance(self.img, str) or isinstance(self.img, np.ndarray):
                return imgZoom(self.img, self.size, False).get('zoom').oriImg
            else:
                res = []
                for i in self.img:
                    res.append(imgZoom(i, 1.0, False).get('zoom').oriImg)
                return res
        else:
            logger.error('Images are not found!')


class NoiseOperator(object):
    def __init__(self, img=None, noiseType: list = []) -> None:
        self.img = img
        self.noiseType = noiseType
        self.defaultNoiseType = set(['gaussian', 'poisson', 's&p', 'speckle'])
        if len(self.noiseType) > 0:
            tmp = set(self.noiseType)
            self.noiseType = list(tmp.intersection(self.defaultNoiseType))

    def setNoiseType(self, val: str):
        if val in self.defaultNoiseType:
            self.noiseType = list(set(self.noiseType).add(val))

    def setImgs(self, imgs):
        self.img = imgs

    def setRandomNoiseType(self, val: bool):
        assert type(
            val
        ) is bool, 'Input of {}.setRandomNoiseType() MUST be a bool value'.format(
            self.__class__)
        if val:
            self.noiseType.clear()

    def do(self):
        if self.img is not None:
            if isinstance(self.img, str) or isinstance(self.img, np.ndarray):
                return imgNoise(self.img, False,
                                self.noiseType).get('noise').oriImg
            else:
                res = []
                for i in self.img:
                    res.append(imgNoise(i, False, []).get('noise').oriImg)
                return res
        else:
            logger.error('Images are not found!')


class RotationOperator(object):
    def __init__(self,
                 img=None,
                 angle: float = 30,
                 scale: float = 1.0) -> None:
        self.img = img
        self.angle = angle
        self.scale = scale

    def setImgs(self, imgs):
        self.img = imgs

    def do(self):
        if self.img is not None:
            if isinstance(self.img, str) or isinstance(self.img, np.ndarray):
                return imgRotation(self.img, self.angle, self.scale,
                                   False).get('rotation').oriImg
            else:
                res = []
                for i in self.img:
                    res.append(
                        imgRotation(i, self.angle, self.scale,
                                    False).get('rotation').oriImg)
                return res
        else:
            logger.error('Images are not found!')


class TranslationOperation(object):
    def __init__(self, img=None, th: int = 0, tv: int = 0) -> None:
        self.img = img
        self.th = th
        self.tv = tv

    def setImgs(self, imgs):
        self.img = imgs

    def do(self):
        if self.img is not None:
            if isinstance(self.img, str) or isinstance(self.img, np.ndarray):
                return imgTranslation(self.img, False, self.th,
                                      self.tv).get('trans').oriImg
            else:
                res = []
                for i in self.img:
                    res.append(
                        imgTranslation(i, False, 0, 0).get('trans').oriImg)
                return res
        else:
            logger.error('Images are not found!')


class FlipOperator(object):
    def __init__(self, img=None) -> None:
        self.img = img

    def setImgs(self, imgs):
        self.img = imgs

    def do(self):
        if self.img is not None:
            if isinstance(self.img, str) or isinstance(self.img, np.ndarray):
                r = imgFlip(self.img, flag=False)
                imgH = r.get('h').oriImg
                imgV = r.get('v').oriImg
                imgHV = r.get('h_v').oriImg
                return [imgH, imgV, imgHV]

            else:
                res = []
                for i in self.img:
                    r = imgFlip(i, flag=False)
                    imgH = r.get('h').oriImg
                    imgV = r.get('v').oriImg
                    imgHV = r.get('h_v').oriImg
                    res.append([imgH, imgV, imgHV])
                return res
        else:
            logger.error('Images are not found!')


class HisteqOperator(object):
    ...


class MainOperatorWithoutLabel(OptionalOperator):
    def __init__(self,
                 img_or_path,
                 saveFile: bool = False,
                 saveDir: str = '') -> None:
        self.imgs = img_or_path
        self.defaults = ['zoom', 'flip', 'noise', 'rotation', 'translation']
        self.augs = []
        self.operations = []
        self.saveFile = saveFile
        self.saveDir = saveDir
        self.optional = False

    def addAugs(self, method: str):
        self.augs.append(method)

    def _help(self):
        print('========  Operation Introduction  =======')
        print('=========== HELP  INFORMATION ===========')
        print("""
            Augumentation library operations. Including:
            1. zoom
            2. noise
            3. rotation
            4. translation
            5. flip

            for 'zoom', parameters list should includes 
            MainOperatorWithoutLabel.setZoomAttributes(size=a float) 

            for 'noise', parameters list should includes 
            MainOperatorWithoutLabel.setNoiseAttributes(noiseType=a list)

            for 'rotation', parameters list should includes 
            MainOperatorWithoutLabel.setRotationOperator(angle=a float,scale=a float)  

            for 'translation',parameters list should includes
            MainOperatorWithoutLabel.setTranslationOperation(th=an int,tv=an int)  

            for 'flip', parameters list should includes
            MainOperatorWithoutLabel.setFlip()

            if you dont like these methods, JUST ignore.
        """)
        print('========= END OF HELP INFORMATION =========')
        print()
        print()
        super()._help()

    def setOptional(self, val: bool):
        assert type(
            val
        ) is bool, 'Input of {}.setOptional() MUST be a bool value'.format(
            self.__class__)
        if val:
            self.optional = val

    def autoAugment(self):
        if len(self.augs) == 0:
            return
        for i in self.augs:
            if i == "zoom":
                _operator = ZoomOperator(None, 1)
                _operator.setRandomSize(True)
                self.operations.insert(0, _operator)

            if i == "noise":
                _operator = NoiseOperator(None, [])
                _operator.setRandomNoiseType(True)
                self.operations.insert(0, _operator)

            if i == "rotation":
                _operator = RotationOperator(None, 30, 1.0)
                self.operations.insert(0, _operator)

            if i == "translation":
                _operator = TranslationOperation(None, 0, 0)
                self.operations.insert(0, _operator)

            if i == "flip":
                self.operations.append(FlipOperator(None))

        if len(self.operations) == 0:
            return

        return self.do()

    def setZoomAttributes(self, **kwargs):
        """Input: size(float, zoom factor)
        """
        if 'zoom' not in self.augs:
            self.augs.append('zoom')
        size = kwargs.get('size', 1.0)
        self.operations.insert(0, ZoomOperator(None, size))

    def setNoiseAttributes(self, **kwargs):
        """Input: noiseType (list, noise type)
        """
        if 'noise' not in self.augs:
            self.augs.append('noise')
        noiseType = kwargs.get('noiseType', [])
        self.operations.insert(0, NoiseOperator(None, noiseType))

    def setRotationOperator(self, **kwargs):
        """Input: 1.angle (float)
                  2.scale (float)
        """
        if 'rotation' not in self.augs:
            self.augs.append('rotation')
        angle = kwargs.get('angle', 30)
        scale = kwargs.get('scale', 1.0)
        self.operations.insert(0, RotationOperator(None, angle, scale))

    def setTranslationOperation(self, **kwargs):
        """Input: 1.th (int)
                  2.tv (int)
        """
        if 'translation' not in self.augs:
            self.augs.append('translation')
        th = kwargs.get('th', 0)
        tv = kwargs.get('tv', 0)
        self.operations.insert(0, TranslationOperation(None, th, tv))

    def setFlip(self):
        if 'flip' not in self.augs:
            self.augs.append('flip')
        self.operations.append(FlipOperator(None))

    def do(self):
        # print(len(self.operations))
        if len(self.augs) == 0:
            logger.info('None methods founds')
            return

        pimgs = self.imgs
        for i in self.operations:
            i.setImgs(pimgs)
            pimgs = i.do()
            gc.collect()

        if not self.saveFile:
            return pimgs
        else:
            # if not os.path.exists(self.saveDir) and self.saveDir != '':
            #     os.mkdir(self.saveDir)
            # else:
            #     logger.error("Provided savedir is not valid")
            #     return
            if self.saveDir == "" or self.saveDir is None:
                logger.error("Provided savedir is not valid")
                return
            
            if not os.path.exists(self.saveDir):
                os.mkdir(self.saveDir)

            if type(self.imgs) is not list:
                if type(self.imgs) is str:
                    filename = os.path.split(self.imgs)[1]
                else:
                    filename = 'test.jpg'
                if isinstance(pimgs, np.ndarray):
                    io.imsave(self.saveDir + os.sep + filename, pimgs)
                else:
                    for i in range(0, len(pimgs)):
                        filename = str(i) + filename
                        io.imsave(self.saveDir + os.sep + filename, pimgs[i])
            else:
                for i in range(len(self.imgs)):
                    if isinstance(self.augs[i], str):
                        filename = os.path.split(i)[1]
                    else:
                        filename = 'test{}.jpg'.format(i)
                    if isinstance(pimgs[i], np.ndarray):
                        io.imsave(self.saveDir + os.sep + filename, pimgs[i])
                    else:
                        for j in range(0, len(pimgs[i])):
                            filename = str(j) + filename
                            io.imsave(self.saveDir + os.sep + filename,
                                      pimgs[i][j])
            logger.info("Done! See {}.".format(self.saveDir))
