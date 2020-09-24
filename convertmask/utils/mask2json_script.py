'''
@lanhuage: python
@Descripttion: 
@version: beta
@Author: xiaoshuyui
@Date: 2020-07-10 10:33:39
LastEditors: xiaoshuyui
LastEditTime: 2020-08-24 10:15:58
'''

from . import getMultiShapes
import glob
import os
from tqdm import tqdm
from .methods.logger import logger

def getJsons(imgPath,maskPath,savePath,yamlPath = ''):
    """
    imgPath: origin image path \n
    maskPath : mask image path \n
    savePath : json file save path \n
    
    >>> getJsons(path-to-your-imgs,path-to-your-maskimgs,path-to-your-jsonfiles) 

    """
    logger.info("currently, only *.jpg supported")
    oriImgs = glob.glob(imgPath+os.sep+'*.jpg')
    maskImgs = glob.glob(maskPath+os.sep+'*.jpg')
    
    for i in tqdm(oriImgs):
        i_mask = i.replace(imgPath,maskPath)
        # print(i)
        getMultiShapes.getMultiShapes(i,i_mask,savePath,yamlPath)

def getXmls(imgPath,maskPath,savePath):
    logger.info("currently, only *.jpg supported")
    oriImgs = glob.glob(imgPath+os.sep+'*.jpg')
    maskImgs = glob.glob(maskPath+os.sep+'*.jpg')
    
    for i in tqdm(oriImgs):
        i_mask = i.replace(imgPath,maskPath)
        # print(i)
        getMultiShapes.getMultiObjs_voc(i,i_mask,savePath)