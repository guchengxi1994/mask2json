'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-09-03 11:41:14
LastEditors: xiaoshuyui
LastEditTime: 2020-09-03 15:37:48
'''
from .splitImg import splitImg_dengbili,reshape_dengbili 
from convertmask.utils.xml2mask import x2m
from skimage import io
from convertmask.utils.getMultiShapes import getMultiShapes
from convertmask.utils.methods.logger import logger
import os
import json
from convertmask.utils.json2xml import j2xConvert
import glob

# save_cache_dir = os.path.abspath(os.path.dirname(os.getcwd())) +os.sep + 'cache'
save_ori_dir = os.path.abspath(os.path.dirname(os.getcwd())) +os.sep + 'ori'
save_xml_dir = os.path.abspath(os.path.dirname(os.getcwd())) +os.sep + 'xml'

# if not os.path.exists(save_cache_dir):
#     os.mkdir(save_cache_dir)

if not os.path.exists(save_ori_dir):
    os.mkdir(save_ori_dir)

if not os.path.exists(save_xml_dir):
    os.mkdir(save_xml_dir)

def convertImgSplit(oriImg:str,mask_or_xml:str,labelpath='',yamlPath:str=''):
    imgName = oriImg.split(os.sep)[-1][:-4]
    logger.warning("multi-process/thread not support!! \n maybe a small error")
    logger.warning("this version is not convenient.it convert mask to json first because i \n have no idea how to modify getMultiShapes.py(getMultiObjs_voc)")
    if mask_or_xml.endswith('xml'):
        _,maskPath = x2m.x2mConvert(mask_or_xml,labelpath,yamlPath)
        maskImg = io.imread(maskPath)

    else:
        maskImg = mask_or_xml
    
    splitMaskImgList = splitImg_dengbili(reshape_dengbili(maskImg),bias=2000,savefile=False)

    splitMaskOriList = splitImg_dengbili(reshape_dengbili(io.imread(oriImg)),bias=2000,savefile=False)

    for i in range(0,len(splitMaskImgList)):
        tmpPath = save_ori_dir+os.sep+imgName+'_{}.jpg'.format(i)
        io.imsave(tmpPath,splitMaskOriList[i])
        tmp = getMultiShapes(tmpPath,splitMaskImgList[i],flag=True,labelYamlPath=yamlPath)
        # print(tmp)
        tmpJsonPath = save_xml_dir+os.sep+imgName+'_{}.json'.format(i)

        with open(tmpJsonPath,'w',encoding='utf-8') as f:
            json.dump(json.loads(tmp),f,indent=4)
        

        j2xConvert(tmpJsonPath)

    
    try:
        jsons = glob.glob(save_xml_dir+os.sep+'*.json')

        # for i in jsons:
        #     os.remove(i)
    except:
        logger.error('delete cache json file failed')


        
        

    
