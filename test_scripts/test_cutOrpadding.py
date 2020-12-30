'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-12-30 09:36:53
LastEditors: xiaoshuyui
LastEditTime: 2020-12-30 11:07:19
'''
import os
import glob
import cv2
import numpy as np
from skimage import io
import xml.etree.ElementTree as ET

import tqdm

defaultSize = 648
defaultFactor = 2.5
imgpath = 'D:\\tensorflow2X\\inv\\alg\\OCR\\1230\\imgs\\'
xmlpath = 'D:\\tensorflow2X\\inv\\alg\\OCR\\1230\\xmls\\'
savePath = 'D:\\tensorflow2X\\inv\\alg\\OCR\\1230\\cvt\\'
imgs = glob.glob(imgpath + '*.jpg')

for i in tqdm.tqdm(imgs):
    img = io.imread(i)
    j = i.replace(imgpath, xmlpath).replace('.jpg', '.xml')
    if os.path.exists(j):
        in_file = open(j)
        tree = ET.parse(in_file)
        root = tree.getroot()
    else:
        tree = None
        root = None

    imgshape = img.shape
    if imgshape[1] / imgshape[0] > defaultFactor:  # cut
        imgT = img[:, 0:int(imgshape[0] * 2.5)]
        io.imsave(i.replace(imgpath, savePath), imgT)
        if root is not None:
            subs = root.findall('object')
            for obj in subs:

            # for obj in root.iter('object'):
                xmlbox = obj.find('bndbox')
                b = (float(xmlbox.find('xmin').text),
                     float(xmlbox.find('xmax').text),
                     float(xmlbox.find('ymin').text),
                     float(xmlbox.find('ymax').text))
                if b[1] > int(2.5 * imgshape[0]):
                    root.remove(obj)

    elif imgshape[1] / imgshape[0] == defaultFactor:
        pass
    else:  #pad
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
        io.imsave(i.replace(imgpath, savePath), imgT)

    if root is not None:
        size = root.find('size')
        size.find('width').text = str(int(imgshape[0] * 2.5))

        tree.write(j)
