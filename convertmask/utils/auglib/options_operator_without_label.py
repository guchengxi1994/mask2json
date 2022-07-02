'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-10-26 10:14:35
LastEditors: xiaoshuyui
LastEditTime: 2020-11-12 10:25:07
'''
import gc
import os

from convertmask.utils.auglib.optional.Operator import (CropOperator,
                                                        DistortOperator,
                                                        InpaintOperator,
                                                        PerspectiveOperator,
                                                        ResizeOperator)
from convertmask.utils.methods.logger import logger
from skimage import io


class MainOptionalOperator(object):
    def __init__(self,
                 img_or_path,
                 saveFile: bool = False,
                 saveDir: str = '') -> None:
        self.imgs = img_or_path
        self.defaults = ['crop', 'distort', 'inpaint', 'perspective', 'resize']
        self.augs = []
        self.operations = []
        self.saveFile = saveFile
        self.saveDir = saveDir

    def _help(self):
        print('=====Optional Operation Introduction=====')
        print('=========== HELP  INFORMATION ===========')
        print("""
            Augumentation library optional operations. Including:
            1. crop
            2. distort
            3. inpaint
            4. perspective
            5. resize
            
            NOTE : These opearions are not suitable for augmenting labels. 

            for 'crop', parameters list should includes 
            MainOptionalOperator.setCropAttributes(rect_or_poly='rect',noise=True,number=2) # or 'poly',False, number less than 4 

            for 'distort', parameters list should includes 
            MainOptionalOperator.setDisortAttributes()

            for 'inpaint', parameters list should includes 
            MainOptionalOperator.setInpaintAttributes(rect_or_poly='poly')  # or 'rect'

            for 'perspective',parameters list should includes
            MainOptionalOperator.setPerspectiveAttributes(factor=0.8)  # float whatever you want

            for 'resize', parameters list should includes
            MainOptionalOperator.setResizeAttributes(height=0.8,width=0.9)

            if you dont like these methods, JUST ignore.
        """)
        print('========= END OF HELP INFORMATION =========')

    def addAugs(self, method: str):
        self.augs.append(method)

    def setCropAttributes(self, **kwargs):
        """Input : 1.rect_or_poly (str,'rect' or 'poly'(short for polygon),crop type),
                   2.noise (bool, use random noise to replace cropped region)
                   3.number (int, crop number)
                   4.convex (bool, short for convexHull)
        """
        if 'crop' not in self.augs:
            self.augs.append('crop')
        rect_or_poly = kwargs.get('rect_or_poly', 'rect')
        noise = kwargs.get('noise', True)
        cropNumber = kwargs.get('number', 1)
        convexHull = kwargs.get('convex', False)
        self.operations.insert(0,
            CropOperator(None, None, rect_or_poly, noise, convexHull,
                         cropNumber))

    def setDisortAttributes(self):
        if 'distort' not in self.augs:
            self.augs.append('distort')
        self.operations.insert(0,DistortOperator(None))

    def setInpaintAttributes(self, **kwargs):
        """Input 1.rect_or_poly (str,'rect' or 'poly'(short for polygon),shape type)
                 2.start (tuple, position of inpaint shape)
        """
        if 'inpaint' not in self.augs:
            self.augs.append('inpaint')
        rect_or_poly = kwargs.get('rect_or_poly', 'rect')
        startPoint = kwargs.get('start', None)
        self.operations.insert(0,InpaintOperator(None, rect_or_poly, startPoint))

    def setPerspectiveAttributes(self, **kwargs):
        """Input: 1. factor (float)
        """
        if 'perspective' not in self.augs:
            self.augs.append('perspective')
        factor = kwargs.get('factor', 0.5)
        self.operations.insert(0,PerspectiveOperator(None, factor))

    def setResizeAttributes(self, **kwargs):
        """Input : 1.height (float)
                   2.width (factor)
        """
        if 'resize' not in self.augs:
            self.augs.append('resize')
        heightFactor = kwargs.get('height', 1.0)
        widthFactor = kwargs.get('width', 1.0)
        self.operations.insert(0,ResizeOperator(None, heightFactor, widthFactor))

    def do(self):
        if len(self.augs) == 0:
            logger.info('None methods founds')
            return

        pimgs = self.imgs
        # print(pimgs)
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
                io.imsave(self.saveDir + os.sep + filename, pimgs)
            else:
                for i in range(len(self.imgs)):
                    if isinstance(self.augs[i], str):
                        filename = os.path.split(i)[1]
                    else:
                        filename = 'test{}.jpg'.format(i)
                    io.imsave(self.saveDir + os.sep + filename, pimgs[i])
            logger.info("Done! See {}.".format(self.saveDir))
