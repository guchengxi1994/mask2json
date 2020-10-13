'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-08-21 10:05:08
LastEditors: xiaoshuyui
LastEditTime: 2020-10-12 15:06:29
'''
from .methods.logger import logger
from . import imgAug
from . import imgAug_nolabel
import glob
import os
from tqdm import tqdm


def imgAug_withLabels(imgPath, labelPath, number=1):
    logger.info("currently, only *.jpg supported")

    oriImgs = glob.glob(imgPath + os.sep +
                        '*.jpg') if os.path.isdir(imgPath) else [imgPath]
    jsonFiles = glob.glob(labelPath + os.sep +
                          '*.json') if os.path.isdir(labelPath) else [
                              labelPath
                          ]

    if type(number) != int:
        logger.error('Augumentation times error.Using 1 as default')
        number = 1
    else:
        if number < 1:
            logger.warning(
                'Augumentation times {} is less than 1.Using 1 as default'.
                format(number))
            number = 1

        for num in range(0, number):
            for i in tqdm(oriImgs):
                i_json = i.replace(
                    imgPath,
                    labelPath) if os.path.isdir(labelPath) else labelPath
                i_json = i_json.replace('.jpg','.xml')
                imgAug.aug_labelme(i, i_json, num=num)
            num += 1


def imgAug_withoutLabels(imgPath, number=1):
    logger.info("currently, only *.jpg supported")

    oriImgs = glob.glob(imgPath + os.sep +
                        '*.jpg') if os.path.isdir(imgPath) else [imgPath]

    if type(number) != int:
        logger.error('Augumentation times error.Using 1 as default')
        number = 1
    else:
        if number < 1:
            logger.warning(
                'Augumentation times {} is less than 1.Using 1 as default'.
                format(number))
            number = 1
        for num in range(0, number):
            for i in tqdm(oriImgs):
                imgAug_nolabel.aug_labelme(i, num=num)
            num += 1


def imgAug_LabelImg(imgPath, xmlpath, number=1):
    logger.info("currently, only *.jpg supported")

    oriImgs = glob.glob(imgPath + os.sep +
                        '*.jpg') if os.path.isdir(imgPath) else [imgPath]
    xmlFiles = glob.glob(xmlpath + os.sep +
                         '*.xml') if os.path.isdir(xmlpath) else [xmlpath]

    if type(number) != int:
        logger.error('Augumentation times error.Using 1 as default')
        number = 1
    else:
        if number < 1:
            logger.warning(
                'Augumentation times {} is less than 1.Using 1 as default'.
                format(number))
            number = 1
        for num in range(0, number):
            for i in tqdm(oriImgs):
                i_xml = i.replace(
                    imgPath, xmlpath) if os.path.isdir(xmlpath) else xmlpath
                i_xml = i_xml.replace('.jpg','.xml')
                imgAug.aug_labelimg(i, i_xml, num=num)
            num += 1
