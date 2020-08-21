'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-08-21 10:05:08
LastEditors: xiaoshuyui
LastEditTime: 2020-08-21 10:42:52
'''
from .methods.logger import logger
from . import imgAug
from . import imgAug_nolabel
import glob
import os
from tqdm import tqdm

def imgAug_withLabels(imgPath,labelPath):
    logger.info("currently, only *.jpg supported")

    oriImgs = glob.glob(imgPath+os.sep+'*.jpg')
    jsonFiles = glob.glob(labelPath+os.sep+'*.json')

    for i in tqdm(oriImgs):
        i_json = i.replace(imgPath,labelPath)

        imgAug.aug_labelme(i,i_json)


def imgAug_withoutLabels(imgPath):
    logger.info("currently, only *.jpg supported")

    oriImgs = glob.glob(imgPath+os.sep+'*.jpg')

    for i in tqdm(oriImgs):

        imgAug_nolabel.aug_labelme(i)



