'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-08-21 10:05:08
LastEditors: xiaoshuyui
LastEditTime: 2020-10-23 09:34:27
'''
import glob
import os
from multiprocessing import Pool

from convertmask import __CPUS__
from convertmask.utils.auglib import img_aug, img_aug_nolabel, img_aug_xmls
from convertmask.utils.methods.logger import logger
from tqdm import tqdm


def proc_xml(img, imgPath, xmlpath, number):
    i_xml = img.replace(imgPath,
                        xmlpath) if os.path.isdir(xmlpath) else xmlpath
    i_xml = i_xml.replace('.jpg', '.xml')
    img_aug_xmls.aug_labelimg(img, i_xml, num=number)


def imgAug_withLabels(imgPath, labelPath, number=1, yamlFilePath=''):
    """
    number : file number you want to generate.
    """
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
                imgPath, labelPath) if os.path.isdir(labelPath) else labelPath
            i_json = i_json.replace('.jpg', '.json')
            img_aug.aug_labelme(i, i_json, num=num, yamlFilePath=yamlFilePath)
        # num += 1


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
            img_aug_nolabel.aug(i, num=num)
        # num += 1


def imgAug_LabelImg(imgPath, xmlpath, number=1):
    """
    number : file number you want to generate.
    """
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

    pool = Pool(__CPUS__ - 1)
    pool_list = []
    for i in oriImgs:
        for num in tqdm(range(0, number)):
            resultspool = pool.apply_async(proc_xml,
                                           (i, imgPath, xmlpath, num))
            pool_list.append(resultspool)

    logger.info('successfully create {} tasks'.format(len(pool_list)))

    for pr in tqdm(pool_list):
        re_list = pr.get()

    # logger.info('Done! See {}'.format())
