'''
lanhuage: python
Descripttion:  this file is just like the imgAug.py ,but don`t need to input a label file(path)
version: beta
Author: xiaoshuyui
Date: 2020-08-21 08:27:05
LastEditors: xiaoshuyui
LastEditTime: 2020-08-21 09:03:30
'''
import sys
sys.path.append('..')
from skimage import io
import skimage.util.noise as snoise
import cv2
from .convert import processor
from .getMultiShapes import getMultiShapes
# from utils.img2base64 import imgEncode
from .methods.img2base64 import imgEncode
from .methods import rmQ
import traceback
# from .entity import *
from .methods.entity import *
import numpy as np
import shutil
import json
# from .logger import logger
from .methods.logger import logger
import random
import os

def do_nothing():
    pass

def imgFlip(oriImg:str,flag=True,flip_list=[1,0,-1]):
    if isinstance(oriImg,str) :
        if os.path.exists(oriImg):
            img = io.imread(oriImg)
        else:
            raise FileNotFoundError('Original image not found')
    else:
        img = oriImg
    
    

    h_ori = cv2.flip(img,1)
    v_ori = cv2.flip(img,0)
    h_v_ori = cv2.flip(img,-1)

    if flag:
        parent_path = os.path.dirname(oriImg)
        if os.path.exists(parent_path+os.sep+'augimgs_'):
            pass
        else:
            os.makedirs(parent_path+os.sep+'augimgs_')
        # fileName = oriLabel.split(os.sep)[-1].replace('.json','') 
        tmp = os.path.splitext(oriImg)[0]
        fileName = tmp.split(os.sep)[-1]

        io.imsave(parent_path+os.sep+'augimgs_'+os.sep+fileName+'_h.jpg',h_ori) if 1 in flip_list else do_nothing
        io.imsave(parent_path+os.sep+'augimgs_'+os.sep+fileName+'_v.jpg',v_ori) if 0 in flip_list else do_nothing
        io.imsave(parent_path+os.sep+'augimgs_'+os.sep+fileName+'_h_v.jpg',h_v_ori) if -1 in flip_list else do_nothing
    
    else:
        d = dict()
        d['h'] = Ori_Pro(h_ori,None)
        d['v'] = Ori_Pro(v_ori,None)
        d['h_v'] = Ori_Pro(h_v_ori,None)

        return d

def imgNoise(oriImg:str,flag=True):
    noise_type = ['gaussian','poisson','s&p','speckle']
    l = np.random.randint(2,size=len(noise_type)).tolist()
    p = list(zip(noise_type,l))

    if isinstance(oriImg,str) :
        if os.path.exists(oriImg):
            img = io.imread(oriImg)
        else:
            raise FileNotFoundError('Original image not found')
    else:
        img = oriImg
    
    if flag:
        parent_path = os.path.dirname(oriImg)
        if os.path.exists(parent_path+os.sep+'augimgs_'):
            pass
        else:
            os.makedirs(parent_path+os.sep+'augimgs_')
        # fileName = oriLabel.split(os.sep)[-1].replace('.json','')
        tmp = os.path.splitext(oriImg)[0]
        fileName = tmp.split(os.sep)[-1]
        io.imsave(parent_path+os.sep+'augimgs_'+os.sep+fileName+'_noise.jpg',img) 
    
    else:
        d = dict()
        d['noise'] = Ori_Pro(img,None)

        return d

        

