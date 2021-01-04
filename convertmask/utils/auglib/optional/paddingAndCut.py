'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2021-01-04 11:31:13
LastEditors: xiaoshuyui
LastEditTime: 2021-01-04 13:34:07
'''
import os
import xml.etree.ElementTree as ET
from glob import glob
import cv2
import numpy as np

import tqdm
from convertmask.utils.auglib.optional.resize import resizeScript
from skimage import io

__defaultSize__ = 648
__defaultFacrot__ = 1


def padCutScript(imgpath: str,
                 xmlpath: str,
                 savepath: str,
                 defaultSize: int = __defaultSize__,
                 defaultFactor: float = __defaultFacrot__,
                 imgExt: list = [
                     "jpg",
                 ],
                 pc: int = 0):
    """
    pc(padding or cut): 0 => middle
                        1 => right/bottom
                        -1 =>  left/top  
    
    defaultFactor : for example, most images are in [h,w] size. but some are not. defaultFactor = w/h (when w>h)

    note: image width is bigger than image height. so resize image to [defaultSize,h] first.   
    """
    imgpaths = []
    for ext in imgExt:
        imgpaths.extend(glob(imgpath + '*.{}'.format(ext)))

    # 1. img width bigger than img height

    for i in tqdm.tqdm(imgpaths):
        oriImg = io.imread(i)
        j = i.replace(imgpath, xmlpath).replace('.jpg', '.xml')
        if os.path.exists(j):
            imgsize = oriImg.shape
            factor = defaultSize / imgsize[0]
            img, path = resizeScript(oriImg,
                                     j,
                                     heightFactor=factor,
                                     widthFactor=factor)
            in_file = ET.parse(path)
            tree = ET.parse(in_file)
            root = tree.getroot()
        else:
            tree = None
            root = None
            img = oriImg

        imgshape = img.shape
        if pc == 1:
            if imgshape[1] / imgshape[0] > defaultFactor:   
                imgT = img[:, 0:int(imgshape[0] * defaultFactor)]
                io.imsave(i.replace(imgpath, savepath), imgT)
                if root is not None:
                    subs = root.findall('object')
                    for obj in subs:
                        xmlbox = obj.find('bndbox')
                        b = (float(xmlbox.find('xmin').text),
                             float(xmlbox.find('xmax').text),
                             float(xmlbox.find('ymin').text),
                             float(xmlbox.find('ymax').text))
                        if b[1] > int(defaultFactor * imgshape[0]):
                            root.remove(obj)
            elif imgshape[1] / imgshape[0] == defaultFactor:
                pass
            else:
                if len(imgshape) == 3:
                    r, g, b = cv2.split(img)
                else:
                    r, g, b = img, img, img
                imgR = np.pad(r, ((0, 0), (0, int(imgshape[0] * 2.5) - imgshape[1])),
                            'constant',
                            constant_values=(255, 255))
                imgG = np.pad(g, ((0, 0), (0, int(imgshape[0] * 2.5) - imgshape[1])),
                            'constant',
                            constant_values=(255, 255))
                imgB = np.pad(b, ((0, 0), (0, int(imgshape[0] * 2.5) - imgshape[1])),
                            'constant',
                            constant_values=(255, 255))
                imgT = cv2.merge([imgR, imgG, imgB])
                io.imsave(i.replace(imgpath, savepath), imgT)
            
            if root is not None:
                size = root.find('size')
                size.find('width').text = str(int(imgshape[0] * 2.5))

                tree.write(j)
