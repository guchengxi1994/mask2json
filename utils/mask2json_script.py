'''
@lanhuage: python
@Descripttion: 
@version: beta
@Author: xiaoshuyui
@Date: 2020-07-10 10:33:39
@LastEditors: xiaoshuyui
@LastEditTime: 2020-07-13 14:21:34
'''

from . import getMultiShapes
import glob
import os

def getJsons(imgPath,maskPath,savePath,yamlPath = ''):
    """
    imgPath: origin image path \n
    maskPath : mask image path \n
    savePath : json file save path \n
    
    >>> getJsons(path-to-your-imgs,path-to-your-maskimgs,path-to-your-jsonfiles) 

    """
    oriImgs = glob.glob(imgPath+os.sep+'*.jpg')
    maskImgs = glob.glob(maskPath+os.sep+'*.jpg')
    
    for i in oriImgs:
        i_mask = i.replace(imgPath,maskPath)
        print(i)

        getMultiShapes.getMultiShapes(i,i_mask,savePath,yamlPath)

def getXmls(imgPath,maskPath,savePath):
    oriImgs = glob.glob(imgPath+os.sep+'*.jpg')
    maskImgs = glob.glob(maskPath+os.sep+'*.jpg')
    
    for i in oriImgs:
        i_mask = i.replace(imgPath,maskPath)
        print(i)

        getMultiShapes.getMultiObjs_voc(i,i_mask,savePath)