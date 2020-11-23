'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-11-18 10:07:24
LastEditors: xiaoshuyui
LastEditTime: 2020-11-20 13:49:30
'''
import cv2
import numpy as np
from skimage import io


def mixup(img1,img2,factor:float=0.5):
    assert (type(img1) is str or type(img1) is np.ndarray),'type of input error'
    assert (type(img2) is str or type(img2) is np.ndarray),'type of input error'
    if isinstance(img1,str):
        img1 = io.imread(img1)
    
    if isinstance(img2,str):
        img2 = io.imread(img2)

    imgShape1 = img1.shape 
    img2 = cv2.resize(img2,(imgShape1[1],imgShape1[0]),interpolation=cv2.INTER_CUBIC)
    
    return np.array(factor*img1 + (1-factor)*img2,dtype=np.uint8)
