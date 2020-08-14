'''
@lanhuage: python
@Descripttion:  (1)get a json file, an origin image \n
                (2)make a convertion \n
                (3)get corresponding json file and converted image
@version: beta
@Author: xiaoshuyui
@Date: 2020-07-17 15:09:27
LastEditors: xiaoshuyui
LastEditTime: 2020-08-14 17:09:54
'''

import sys
sys.path.append('..')
import warnings
from skimage import io
import cv2
import os
from utils.convert import processor
from utils.getMultiShapes import getMultiShapes
from utils import rmQ
import traceback
from .entity import *


def imgFlip(oriImg:str,oriLabel:str,flip_list=[1,0,-1],flag=True):
    """
    flipList: flip type. see cv2.flip :
    1: 水平翻转 \n
    0: 垂直翻转 \n
    -1: 同时翻转 \n
    >>> import cv2
    >>> help(cv2.flip)
    """
    if isinstance(oriImg,str) :
        if os.path.exists(oriImg):
            img = io.imread(oriImg)
        else:
            raise FileNotFoundError('Original image not found')
    else:
        img = oriImg

    try:
        if len(flip_list)>1 and (1 in flip_list or 0 in flip_list or -1 in flip_list):
            mask = processor(oriLabel,flag=True)
            # print(type(mask))
            h_ori = cv2.flip(img,1)
            v_ori = cv2.flip(img,0)
            h_v_ori = cv2.flip(img,-1)

            h_mask = cv2.flip(mask,1) if 1 in flip_list else None
            v_mask = cv2.flip(mask,0) if 0 in flip_list else None
            h_v_mask = cv2.flip(mask,-1) if -1 in flip_list else None

            """
            maybe dict zip is better :)
            """

            if flag:
                parent_path = os.path.dirname(oriLabel)
                if os.path.exists(parent_path+os.sep+'jsons_'):
                    pass
                else:
                    os.makedirs(parent_path+os.sep+'jsons_')
                fileName = oriLabel.split(os.sep)[-1].replace('.json','')

                io.imsave(parent_path+os.sep+'jsons_'+os.sep+fileName+'_h.jpg',h_ori) if 1 in flip_list else print()
                io.imsave(parent_path+os.sep+'jsons_'+os.sep+fileName+'_v.jpg',v_ori) if 0 in flip_list else print()
                io.imsave(parent_path+os.sep+'jsons_'+os.sep+fileName+'_h_v.jpg',h_v_ori) if -1 in flip_list else print()


                # h_j = getMultiShapes(parent_path+os.sep+'jsons_'+os.sep+fileName+'_h.jpg',h_mask,flag=True,labelYamlPath='') if h_mask is not None else None
                h_j = getMultiShapes(parent_path+os.sep+'jsons_'+os.sep+fileName+'_h.jpg',h_mask,flag=True,labelYamlPath='D:\\testALg\\mask2json\\mask2json\\multi_objs_json\\info.yaml')
                v_j = getMultiShapes(parent_path+os.sep+'jsons_'+os.sep+fileName+'_v.jpg',v_mask,flag=True,labelYamlPath='') if v_mask is not None else None
                h_v_j = getMultiShapes(parent_path+os.sep+'jsons_'+os.sep+fileName+'_h_v.jpg',h_v_mask,flag=True,labelYamlPath='') if h_v_mask is not None else None

                for saveJsonPath in [parent_path+os.sep+'jsons_'+os.sep+fileName+'_h.json',
                                    parent_path+os.sep+'jsons_'+os.sep+fileName+'_v.json',
                                    parent_path+os.sep+'jsons_'+os.sep+fileName+'_H_V.json']:
                    
                    # if saveJsonPath is not None:
                        # print(saveJsonPath)
                    if saveJsonPath.endswith('_h.json')  :   
                        if h_j is not None:
                            with open(saveJsonPath,'w') as f:
                                f.write(h_j)
                        else:
                            pass
                    elif saveJsonPath.endswith('_v.json')  :  
                        if v_j is not None:
                            with open(saveJsonPath,'w') as f:
                                f.write(v_j)
                        else:
                            pass
                    elif saveJsonPath.endswith('_H_V.json') :
                        if h_v_j is not None:
                            with open(saveJsonPath,'w') as f:
                                f.write(h_v_j) 
                        else:
                            pass
                
                    rmQ.rm(saveJsonPath) if os.path.exists(saveJsonPath) else print()
                
                return ""
            else:

                d = dict()
                d['h'] = Ori_Pro(h_ori,h_mask)
                d['v'] = Ori_Pro(v_ori,v_mask)
                d['h_v'] = Ori_Pro(h_v_ori,h_v_mask)

                return d
                
        else:
            warnings.warn("<===== param:flip_list is not valid =====>")



    except Exception :
        # print(e)
        print(traceback.format_exc())


            
    




def aug_labelme(filepath,jsonpath,augs:list):
    """
    augs: ['flip','noise','affine','rotate','...']
    """

    default_augs =set(['flip','noise','affine','rotate'])
    tmp = set(augs)
    tmp = tmp.difference(default_augs)

    if len(list(tmp))>0:
        warnings.WarningMessage("some methods not supported right now")
        methods = list(default_augs & set(augs))
    else:
        methods = augs

    if not len(methods)>0:
        pass
    else:
        pass





