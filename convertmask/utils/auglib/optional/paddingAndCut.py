'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2021-01-04 11:31:13
LastEditors: xiaoshuyui
LastEditTime: 2021-02-01 13:23:47
'''
import math
import os
try:
    import defusedxml.ElementTree as ET
except:
    import xml.etree.ElementTree as ET
from glob import glob
from multiprocessing import Pool

import cv2
import numpy as np
import tqdm
from convertmask import __CPUS__, baseDecorate
from convertmask.utils.auglib.optional.resize import resize_img, resizeScript
from skimage import io

__defaultSize__ = 648
__defaultFacrot__ = 2.5


@baseDecorate('this function is untested.')
def specificPadCutScript(imgpath: str,
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

    for i in tqdm.tqdm(imgpaths):
        oriImg = io.imread(i)
        imgsize = oriImg.shape
        _, ext = os.path.splitext(i)
        j = i.replace(imgpath, xmlpath).replace(ext, '.xml')
        # j = i.replace(imgpath, xmlpath).replace('.jpg', '.xml')
        if imgsize[1] >= imgsize[0]:  # 1. img width bigger than img height
            if os.path.exists(j):
                factor = defaultSize / imgsize[0]
                img, path = resizeScript(oriImg,
                                         j,
                                         heightFactor=factor,
                                         widthFactor=factor)
                # in_file = ET.parse(path)
                # tree = ET.parse(in_file)
                tree = ET.parse(path)
                root = tree.getroot()
            else:
                tree = None
                root = None
                img = oriImg

            imgshape = img.shape

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

                if pc == 1:
                    imgR = np.pad(
                        r,
                        ((0, 0),
                         (0, int(imgshape[0] * defaultFactor) - imgshape[1])),
                        'constant',
                        constant_values=(255, 255))
                    imgG = np.pad(
                        g,
                        ((0, 0),
                         (0, int(imgshape[0] * defaultFactor) - imgshape[1])),
                        'constant',
                        constant_values=(255, 255))
                    imgB = np.pad(
                        b,
                        ((0, 0),
                         (0, int(imgshape[0] * defaultFactor) - imgshape[1])),
                        'constant',
                        constant_values=(255, 255))
                elif pc == -1:
                    imgR = np.pad(
                        r,
                        ((0, 0),
                         (int(imgshape[0] * defaultFactor) - imgshape[1], 0)),
                        'constant',
                        constant_values=(255, 255))
                    imgG = np.pad(
                        g,
                        ((0, 0),
                         (int(imgshape[0] * defaultFactor) - imgshape[1], 0)),
                        'constant',
                        constant_values=(255, 255))
                    imgB = np.pad(
                        b,
                        ((0, 0),
                         (int(imgshape[0] * defaultFactor) - imgshape[1], 0)),
                        'constant',
                        constant_values=(255, 255))
                    if root is not None:
                        subs = root.findall('object')
                        for obj in subs:
                            xmlbox = obj.find('bndbox')
                            xmlbox.find('xmin').text = str(
                                int(xmlbox.find('xmin').text) +
                                int(imgshape[0] * defaultFactor) - imgshape[1])
                            xmlbox.find('xmax').text = str(
                                int(xmlbox.find('xmax').text) +
                                int(imgshape[0] * defaultFactor) - imgshape[1])

                else:
                    imgR = np.pad(
                        r, ((0, 0),
                            int((imgshape[0] * defaultFactor - imgshape[1]) *
                                0.5),
                            int((imgshape[0] * defaultFactor - imgshape[1]) *
                                0.5)),
                        'constant',
                        constant_values=(255, 255))
                    imgG = np.pad(
                        g, ((0, 0),
                            int((imgshape[0] * defaultFactor - imgshape[1]) *
                                0.5),
                            int((imgshape[0] * defaultFactor - imgshape[1]) *
                                0.5)),
                        'constant',
                        constant_values=(255, 255))
                    imgB = np.pad(
                        b, ((0, 0),
                            int((imgshape[0] * defaultFactor - imgshape[1]) *
                                0.5),
                            int((imgshape[0] * defaultFactor - imgshape[1]) *
                                0.5)),
                        'constant',
                        constant_values=(255, 255))

                    if root is not None:
                        subs = root.findall('object')
                        for obj in subs:
                            xmlbox = obj.find('bndbox')
                            xmlbox.find('xmin').text = str(
                                int(xmlbox.find('xmin').text) +
                                int((imgshape[0] * defaultFactor) -
                                    imgshape[1]) * 0.5)
                            xmlbox.find('xmax').text = str(
                                int(xmlbox.find('xmax').text) +
                                int((imgshape[0] * defaultFactor) -
                                    imgshape[1]) * 0.5)

                imgT = cv2.merge([imgR, imgG, imgB])
                io.imsave(i.replace(imgpath, savepath), imgT)

            if root is not None:
                size = root.find('size')
                size.find('width').text = str(int(imgshape[0] * 2.5))
                tree.write(j)

        else:
            if os.path.exists(j):
                factor = defaultSize / imgsize[0]
                img, path = resizeScript(oriImg,
                                         j,
                                         heightFactor=factor,
                                         widthFactor=factor)
                # in_file = ET.parse(path)
                # tree = ET.parse(in_file)
                tree = ET.parse(path)
                root = tree.getroot()
            else:
                tree = None
                root = None
                img = oriImg

            imgshape = img.shape

            if imgshape[0] / imgshape[1] > defaultFactor:
                imgT = img[0:int(imgshape[1] * defaultFactor), :]
                io.imsave(i.replace(imgpath, savepath), imgT)
                if root is not None:
                    subs = root.findall('object')
                    for obj in subs:
                        xmlbox = obj.find('bndbox')
                        b = (float(xmlbox.find('xmin').text),
                             float(xmlbox.find('xmax').text),
                             float(xmlbox.find('ymin').text),
                             float(xmlbox.find('ymax').text))
                        if b[3] > int(defaultFactor * imgshape[1]):
                            root.remove(obj)
            elif imgshape[0] / imgshape[1] == defaultFactor:
                pass
            else:
                if len(imgshape) == 3:
                    r, g, b = cv2.split(img)
                else:
                    r, g, b = img, img, img

                if pc == 1:
                    imgR = np.pad(
                        r,
                        ((0, int(imgshape[0] * defaultFactor) - imgshape[1]),
                         (0, 0)),
                        'constant',
                        constant_values=(255, 255))
                    imgG = np.pad(
                        g,
                        ((0, int(imgshape[0] * defaultFactor) - imgshape[1]),
                         (0, 0)),
                        'constant',
                        constant_values=(255, 255))
                    imgB = np.pad(
                        b,
                        ((0, int(imgshape[0] * defaultFactor) - imgshape[1]),
                         (0, 0)),
                        'constant',
                        constant_values=(255, 255))
                elif pc == -1:
                    imgR = np.pad(
                        r,
                        ((int(imgshape[0] * defaultFactor) - imgshape[1], 0),
                         (0, 0)),
                        'constant',
                        constant_values=(255, 255))
                    imgG = np.pad(
                        g,
                        ((int(imgshape[0] * defaultFactor) - imgshape[1], 0),
                         (0, 0)),
                        'constant',
                        constant_values=(255, 255))
                    imgB = np.pad(
                        b,
                        ((int(imgshape[0] * defaultFactor) - imgshape[1], 0),
                         (0, 0)),
                        'constant',
                        constant_values=(255, 255))
                    if root is not None:
                        subs = root.findall('object')
                        for obj in subs:
                            xmlbox = obj.find('bndbox')
                            xmlbox.find('ymin').text = str(
                                int(xmlbox.find('ymin').text) +
                                int(imgshape[1] * defaultFactor) - imgshape[0])
                            xmlbox.find('yman').text = str(
                                int(xmlbox.find('yman').text) +
                                int(imgshape[1] * defaultFactor) - imgshape[0])

                else:
                    imgR = np.pad(
                        r, (int(
                            (imgshape[0] * defaultFactor - imgshape[1]) * 0.5),
                            int((imgshape[0] * defaultFactor - imgshape[1]) *
                                0.5), (0, 0)),
                        'constant',
                        constant_values=(255, 255))
                    imgG = np.pad(
                        g, (int(
                            (imgshape[0] * defaultFactor - imgshape[1]) * 0.5),
                            int((imgshape[0] * defaultFactor - imgshape[1]) *
                                0.5), (0, 0)),
                        'constant',
                        constant_values=(255, 255))
                    imgB = np.pad(
                        b, (int(
                            (imgshape[0] * defaultFactor - imgshape[1]) * 0.5),
                            int((imgshape[0] * defaultFactor - imgshape[1]) *
                                0.5), (0, 0)),
                        'constant',
                        constant_values=(255, 255))

                    if root is not None:
                        subs = root.findall('object')
                        for obj in subs:
                            xmlbox = obj.find('bndbox')
                            xmlbox.find('ymin').text = str(
                                int(xmlbox.find('ymin').text) +
                                int((imgshape[1] * defaultFactor) -
                                    imgshape[0]) * 0.25)
                            xmlbox.find('ymax').text = str(
                                int(xmlbox.find('ymax').text) +
                                int((imgshape[1] * defaultFactor) -
                                    imgshape[0]) * 0.25)

                imgT = cv2.merge([imgR, imgG, imgB])
                io.imsave(i.replace(imgpath, savepath), imgT)

            if root is not None:
                size = root.find('size')
                size.find('width').text = str(int(imgshape[0] * 2.5))
                tree.write(j)


@baseDecorate('this function is untested.')
def autoPaddingScript(imgpath: str,
                      xmlpath: str,
                      savepath: str,
                      defaultSize: int = __defaultSize__,
                      imgExt: list = [
                          "jpg",
                      ],
                      padding: int = 1):
    imgpaths = []
    for ext in imgExt:
        imgpaths.extend(glob(imgpath + '*.{}'.format(ext)))

    for i in tqdm.tqdm(imgpaths):
        oriImg = io.imread(i)
        imgsize = oriImg.shape
        _, ext = os.path.splitext(i)
        j = i.replace(imgpath, xmlpath).replace(ext, '.xml')

        if imgsize[0] > imgsize[1]:  # width<height
            hFactor = defaultSize / imgsize[0]
            wFactor = hFactor
        else:
            wFactor = defaultSize / imgsize[1]
            hFactor = wFactor
        if os.path.exists(j):
            img, path = resizeScript(oriImg,
                                     j,
                                     heightFactor=hFactor,
                                     widthFactor=wFactor)
            # in_file = ET.parse(path)
            tree = ET.parse(path)
            root = tree.getroot()
        else:
            img = resize_img(oriImg, hFactor, wFactor)

            tree = None
            root = None

        height, width = img.shape[0], img.shape[1]
        f = 1 if img.shape[0] <= img.shape[1] else 0  # f == 1 ,height<=width

        paddingSize = defaultSize - height if f == 1 else defaultSize - width

        if len(img.shape) == 3:
            r, g, b = cv2.split(img)
        else:
            r, g, b = img, img, img

        if f == 1:
            if padding == 1:
                imgR = np.pad(r, ((0, 0), (0, paddingSize)),
                              'constant',
                              constant_values=(255, 255))
                imgG = np.pad(g, ((0, 0), (0, paddingSize)),
                              'constant',
                              constant_values=(255, 255))
                imgB = np.pad(b, ((0, 0), (0, paddingSize)),
                              'constant',
                              constant_values=(255, 255))
            elif padding == -1:
                imgR = np.pad(r, ((0, 0), (paddingSize, 0)),
                              'constant',
                              constant_values=(255, 255))
                imgG = np.pad(g, ((0, 0), (paddingSize, 0)),
                              'constant',
                              constant_values=(255, 255))
                imgB = np.pad(b, ((0, 0), (paddingSize, 0)),
                              'constant',
                              constant_values=(255, 255))
                if root is not None:
                    subs = root.findall('object')
                    for obj in subs:
                        xmlbox = obj.find('bndbox')
                        xmlbox.find('xmin').text = str(
                            int(xmlbox.find('xmin').text) + paddingSize)
                        xmlbox.find('xmax').text = str(
                            int(xmlbox.find('xmax').text) + paddingSize)
            else:
                if paddingSize % 2 == 0:
                    imgR = np.pad(
                        r, ((0, 0),
                            (int(0.5 * paddingSize), int(0.5 * paddingSize))),
                        'constant',
                        constant_values=(255, 255))
                    imgG = np.pad(
                        g, ((0, 0),
                            (int(0.5 * paddingSize), int(0.5 * paddingSize))),
                        'constant',
                        constant_values=(255, 255))
                    imgB = np.pad(
                        b, ((0, 0),
                            (int(0.5 * paddingSize), int(0.5 * paddingSize))),
                        'constant',
                        constant_values=(255, 255))

                else:
                    imgR = np.pad(r, ((0, 0), (int(
                        0.5 * paddingSize), 1 + int(0.5 * paddingSize))),
                                  'constant',
                                  constant_values=(255, 255))
                    imgG = np.pad(g, ((0, 0), (int(
                        0.5 * paddingSize), 1 + int(0.5 * paddingSize))),
                                  'constant',
                                  constant_values=(255, 255))
                    imgB = np.pad(b, ((0, 0), (int(
                        0.5 * paddingSize), 1 + int(0.5 * paddingSize))),
                                  'constant',
                                  constant_values=(255, 255))

                if root is not None:
                    subs = root.findall('object')
                    for obj in subs:
                        xmlbox = obj.find('bndbox')
                        xmlbox.find('xmin').text = str(
                            int(
                                int(xmlbox.find('xmin').text) +
                                0.5 * paddingSize))
                        xmlbox.find('xmax').text = str(
                            int(
                                int(xmlbox.find('xmax').text) +
                                0.5 * paddingSize))

        else:
            if padding == 1:
                imgR = np.pad(r, ((0, paddingSize), (0, 0)),
                              'constant',
                              constant_values=(255, 255))
                imgG = np.pad(g, ((0, paddingSize), (0, 0)),
                              'constant',
                              constant_values=(255, 255))
                imgB = np.pad(b, ((0, paddingSize), (0, 0)),
                              'constant',
                              constant_values=(255, 255))
            elif padding == -1:
                imgR = np.pad(r, ((paddingSize, 0), (0, 0)),
                              'constant',
                              constant_values=(255, 255))
                imgG = np.pad(g, ((paddingSize, 0), (0, 0)),
                              'constant',
                              constant_values=(255, 255))
                imgB = np.pad(b, ((paddingSize, 0), (0, 0)),
                              'constant',
                              constant_values=(255, 255))
                if root is not None:
                    subs = root.findall('object')
                    for obj in subs:
                        xmlbox = obj.find('bndbox')
                        xmlbox.find('ymin').text = str(
                            int(xmlbox.find('ymin').text) + paddingSize)
                        xmlbox.find('ymax').text = str(
                            int(xmlbox.find('ymax').text) + paddingSize)
            else:
                if paddingSize % 2 == 0:
                    imgR = np.pad(
                        r, ((int(0.5 * paddingSize), int(0.5 * paddingSize)),
                            (0, 0)),
                        'constant',
                        constant_values=(255, 255))
                    imgG = np.pad(
                        g, ((int(0.5 * paddingSize), int(0.5 * paddingSize)),
                            (0, 0)),
                        'constant',
                        constant_values=(255, 255))
                    imgB = np.pad(
                        b, ((int(0.5 * paddingSize), int(0.5 * paddingSize)),
                            (0, 0)),
                        'constant',
                        constant_values=(255, 255))

                else:
                    imgR = np.pad(
                        r,
                        ((int(0.5 * paddingSize), 1 + int(0.5 * paddingSize)),
                         (0, 0)),
                        'constant',
                        constant_values=(255, 255))
                    imgG = np.pad(
                        g,
                        ((int(0.5 * paddingSize), 1 + int(0.5 * paddingSize)),
                         (0, 0)),
                        'constant',
                        constant_values=(255, 255))
                    imgB = np.pad(
                        b,
                        ((int(0.5 * paddingSize), 1 + int(0.5 * paddingSize)),
                         (0, 0)),
                        'constant',
                        constant_values=(255, 255))

                if root is not None:
                    subs = root.findall('object')
                    for obj in subs:
                        xmlbox = obj.find('bndbox')
                        xmlbox.find('ymin').text = str(
                            int(
                                int(xmlbox.find('ymin').text) +
                                0.5 * paddingSize))
                        xmlbox.find('ymax').text = str(
                            int(
                                int(xmlbox.find('ymax').text) +
                                0.5 * paddingSize))

        imgT = cv2.merge([imgR, imgG, imgB])
        io.imsave(i.replace(imgpath, savepath), imgT)

        if root is not None:
            size = root.find('size')
            size.find('width').text = defaultSize
            size.find('height').text = defaultSize
            tree.write(j)


def padImgForSplit(i: str, imgpath, savepath, saveFile):
    oriImg = io.imread(i)
    imgsize = oriImg.shape

    flag = imgsize[0] % 2 == 0

    if len(oriImg.shape) == 3:
        r, g, b = cv2.split(oriImg)
    else:
        r, g, b = oriImg, oriImg, oriImg

    if flag:
        padWidth = int(math.ceil(imgsize[1] / imgsize[0]) * imgsize[0])
    else:
        padWidth = int(
            math.ceil(imgsize[1] / (imgsize[0] + 1)) * (imgsize[0] + 1))

    if imgsize[1] < padWidth:
        paddingSize = padWidth - imgsize[1]
        if flag:
            imgR = np.pad(r, ((0, 0), (0, paddingSize)),
                          'constant',
                          constant_values=(255, 255))
            imgG = np.pad(g, ((0, 0), (0, paddingSize)),
                          'constant',
                          constant_values=(255, 255))
            imgB = np.pad(b, ((0, 0), (0, paddingSize)),
                          'constant',
                          constant_values=(255, 255))
        else:
            imgR = np.pad(r, ((0, 1), (0, paddingSize)),
                          'constant',
                          constant_values=(255, 255))
            imgG = np.pad(g, ((0, 1), (0, paddingSize)),
                          'constant',
                          constant_values=(255, 255))
            imgB = np.pad(b, ((0, 1), (0, paddingSize)),
                          'constant',
                          constant_values=(255, 255))

        imgT = cv2.merge([imgR, imgG, imgB])
        if saveFile:
            io.imsave(i.replace(imgpath, savepath), imgT)
        else:
            return imgT


@baseDecorate(
    'this method is used to split images to small images after padding.')
def padForSplitScript(imgpath: str,
                      savepath: str,
                      imgExt: list = [
                          "jpg",
                      ],
                      multiprocesses=True,
                      saveFile=True):
    imgpaths = []
    for ext in imgExt:
        imgpaths.extend(glob(imgpath + '*.{}'.format(ext)))

    if not multiprocesses:
        for i in tqdm.tqdm(imgpaths):
            padImgForSplit(i, imgpath, savepath, saveFile)
    else:
        pool = Pool(__CPUS__ - 1)
        pool_list = []

        for i in tqdm.tqdm(imgpaths):
            resultPool = pool.apply_async(padImgForSplit,
                                          (i, imgpath, savepath, saveFile))
            pool_list.append(resultPool)

        for pr in tqdm.tqdm(pool_list):
            pr.get()
