'''
@lanhuage: python
@Descripttion:  (1)get a json file, an origin image \n
                (2)make a convertion \n
                (3)get corresponding json file and converted image
@version: beta
@Author: xiaoshuyui
@Date: 2020-07-17 15:09:27
@LastEditors: xiaoshuyui
@LastEditTime: 2020-07-17 17:47:22
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



def imgFlip(oriImg:str,oriLabel:str,flip_list=[1,0,-1]):
    """
    flipList: flip type. see cv2.flip
    1: 水平翻转 \n
    0: 垂直翻转 \n
    -1: 同时翻转
    """
    if isinstance(oriImg,str) :
        if os.path.exists(oriImg):
            img = io.imread(oriImg)
        else:
            raise FileNotFoundError('Original image not found')
    else:
        img = oriImg

    try:
        mask = processor(oriLabel,flag=True)
        # print(type(mask))
        h_ori = cv2.flip(img,1)
        v_ori = cv2.flip(img,0)
        h_v_ori = cv2.flip(img,-1)

        parent_path = os.path.dirname(oriLabel)
        if os.path.exists(parent_path+os.sep+'jsons_'):
            pass
        else:
            os.makedirs(parent_path+os.sep+'jsons_')

        fileName = oriLabel.split(os.sep)[-1].replace('.json','')
        io.imsave(parent_path+os.sep+'jsons_'+os.sep+fileName+'_h.jpg',h_ori)
        io.imsave(parent_path+os.sep+'jsons_'+os.sep+fileName+'_v.jpg',v_ori)
        io.imsave(parent_path+os.sep+'jsons_'+os.sep+fileName+'_h_v.jpg',h_v_ori)

        h_mask = cv2.flip(mask,1)
        v_mask = cv2.flip(mask,0)
        h_v_mask = cv2.flip(mask,-1)

        h_j = getMultiShapes(parent_path+os.sep+'jsons_'+os.sep+fileName+'_h.jpg',h_mask,flag=True,labelYamlPath='D:\\testALg\\mask2json\\mask2json\\multi_objs_json\\info.yaml')
        v_j = getMultiShapes(parent_path+os.sep+'jsons_'+os.sep+fileName+'_v.jpg',v_mask,flag=True,labelYamlPath='D:\\testALg\\mask2json\\mask2json\\multi_objs_json\\info.yaml')
        h_v_j = getMultiShapes(parent_path+os.sep+'jsons_'+os.sep+fileName+'_h_v.jpg',h_v_mask,flag=True,labelYamlPath='D:\\testALg\\mask2json\\mask2json\\multi_objs_json\\info.yaml')

        """
        maybe dict zip is better :)
        """

        for saveJsonPath in [parent_path+os.sep+'jsons_'+os.sep+fileName+'_h.json',
                            parent_path+os.sep+'jsons_'+os.sep+fileName+'_v.json',
                            parent_path+os.sep+'jsons_'+os.sep+fileName+'_H_V.json']:
            
            
            if saveJsonPath.endswith('_h.json'):
                with open(saveJsonPath,'w') as f:
                    f.write(h_j)
            elif saveJsonPath.endswith('_v.json'):
                with open(saveJsonPath,'w') as f:
                    f.write(v_j)
            else:
                with open(saveJsonPath,'w') as f:
                    f.write(h_v_j)
    
            rmQ.rm(saveJsonPath)



        


        
    except Exception as e:
        print(e)


            
    




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





