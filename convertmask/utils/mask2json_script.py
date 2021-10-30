'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-07-10 10:33:39
LastEditors: xiaoshuyui
LastEditTime: 2021-01-05 10:21:49
'''

import glob
import os

from tqdm import tqdm

from convertmask.utils.methods import get_multi_shapes
from convertmask.utils.methods.logger import logger


def getJsons(imgPath, maskPath, savePath, yamlPath=''):
    """
    imgPath: origin image path \n
    maskPath : mask image path \n
    savePath : json file save path \n
    
    >>> getJsons(path-to-your-imgs,path-to-your-maskimgs,path-to-your-jsonfiles) 

    """
    logger.info("currently, only *.jpg supported")

    if os.path.isfile(imgPath):
        get_multi_shapes.getMultiShapes(imgPath, maskPath, savePath, yamlPath)

    elif os.path.isdir(imgPath):
        oriImgs = glob.glob(imgPath + os.sep + '*.jpg')
        maskImgs = glob.glob(maskPath + os.sep + '*.jpg')
        for i in tqdm(oriImgs):
            i_mask = i.replace(imgPath, maskPath)
            if os.path.exists(i_mask):
                # print(i)
                get_multi_shapes.getMultiShapes(i, i_mask, savePath, yamlPath)
            else:
                logger.warning('corresponding mask image not found!')
                continue
    else:
        logger.error('input error. got [{},{},{},{}]. file maybe missing.'.format(
            imgPath, maskPath, savePath, yamlPath))
    logger.info('Done! See here. {}'.format(savePath))


def getXmls(imgPath, maskPath, savePath):
    logger.info("currently, only *.jpg supported")

    if os.path.isfile(imgPath):
        get_multi_shapes.getMultiObjs_voc(imgPath, maskPath, savePath)
    elif os.path.isdir(imgPath):
        oriImgs = glob.glob(imgPath + os.sep + '*.jpg')
        maskImgs = glob.glob(maskPath + os.sep + '*.jpg')

        for i in tqdm(oriImgs):
            i_mask = i.replace(imgPath, maskPath)
            # print(i)
            if os.path.exists(i_mask):
                get_multi_shapes.getMultiObjs_voc(i, i_mask, savePath)
            else:
                logger.warning('corresponding mask image not found!')
                continue
    else:
        logger.error('input error. got [{},{},{}]. file maybe missing.'.format(
            imgPath, maskPath, savePath))
    logger.info('Done! See here. {}'.format(savePath))
