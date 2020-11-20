import datetime
import os
import random
import xml.etree.ElementTree as ET

import cv2
import numpy as np
import skimage
from convertmask.utils.auglib.optional.resize import resize_img
from convertmask.utils.img2xml.processor_multiObj import img2xml_multiobj
from convertmask.utils.methods.logger import logger
from convertmask.utils.xml2yolo.xml2yolo import convert as x2yVert
from convertmask.utils.yolo2xml.yolo2xml import convert as y2xVert
from skimage import io

from .resize import resizeScript


def getMeanSize(imgs: list):
    height = []
    width = []
    for i in imgs:
        height.append(i.shape[0])
        width.append(i.shape[1])

    return int(np.mean(height)), int(np.mean(width))


def getName(xmls: list):
    # print(str(i))
    s = str(datetime.datetime.now())
    for i in xmls:
        s += i
    return str(abs(hash(s)))


def mosiacScript(imgs: list, xmls: list, savePath: str, flag=False):
    heightFactor = random.uniform(0.3, 0.7)
    widthFactor = random.uniform(0.3, 0.7)

    if not type(imgs) is list or not type(xmls) is list:
        logger.error('Input must be list!')
        return

    # imgs
    if len(imgs) == 0:
        logger.error('None image found!')
        return

    if len(imgs) == 1:
        for _ in range(0, 3):
            imgs.append(imgs[0])

    if len(imgs) == 2:
        for _ in range(0, 2):
            imgs.append(imgs[0])

    if len(imgs) == 3:
        for _ in range(0, 1):
            imgs.append(imgs[0])

    # xmls
    if len(xmls) == 0:
        logger.error('None xml found!')
        return

    if len(xmls) == 1:
        for _ in range(0, 3):
            xmls.append(xmls[0])

    if len(xmls) == 2:
        for _ in range(0, 2):
            xmls.append(xmls[0])

    if len(xmls) == 3:
        for _ in range(0, 1):
            xmls.append(xmls[0])

    imgname = getName(xmls)
    folder = savePath
    mHeight, mWidth = getMeanSize(imgs)
    mosiacImg = mosiac_img(imgs, heightFactor, widthFactor)
    objs = []
    imgshape = mosiacImg.shape
    for idx in range(len(xmls)):
        in_file = open(xmls[idx])
        tree = ET.parse(in_file)
        root = tree.getroot()

        for o in root.iter('object'):
            obj = dict()
            name = o.find('name').text
            difficult = 0
            xmlbox = o.find('bndbox')
            b = (float(xmlbox.find('xmin').text),
                 float(xmlbox.find('xmax').text),
                 float(xmlbox.find('ymin').text),
                 float(xmlbox.find('ymax').text))
            # print('===========================')
            # print(b)
            bb = x2yVert((mWidth, mHeight), b)
            x, y, w, h = bb[0], bb[1], bb[2], bb[3]
            if idx == 0:
                bbox = y2xVert(
                    (imgshape[1] * widthFactor, imgshape[0] * heightFactor), x,
                    y, w, h)

            elif idx == 1:
                bbox = y2xVert((imgshape[1] *
                                (1 - widthFactor), imgshape[0] * heightFactor),
                               x, y, w, h)
                bbox[0] = bbox[0] + int(widthFactor * imgshape[1])
                bbox[1] = bbox[1] + int(widthFactor * imgshape[1])

            elif idx == 2:
                bbox = y2xVert((imgshape[1] * widthFactor, imgshape[0] *
                                (1 - heightFactor)), x, y, w, h)
                bbox[2] = bbox[2] + int(heightFactor * imgshape[0])
                bbox[3] = bbox[3] + int(heightFactor * imgshape[0])

            else:
                bbox = y2xVert((imgshape[1] * (1 - widthFactor), imgshape[0] *
                                (1 - heightFactor)), x, y, w, h)
                bbox[0] = bbox[0] + int(widthFactor * imgshape[1])
                bbox[2] = bbox[2] + int(heightFactor * imgshape[0])
                bbox[1] = bbox[1] + int(widthFactor * imgshape[1])
                bbox[3] = bbox[3] + int(heightFactor * imgshape[0])

            # print(x, y, w, h)
            # w = w
            # h = h
            # bbox = y2xVert((imgshape[1],imgshape[0]), x, y, w, h)

            tmp = dict()
            tmp['xmin'] = str(int(bbox[0]))
            tmp['ymin'] = str(int(bbox[2]))
            tmp['xmax'] = str(int(bbox[1]))
            tmp['ymax'] = str(int(bbox[3]))
            obj['name'] = name
            obj['difficult'] = difficult
            obj['bndbox'] = tmp
            del tmp
            objs.append(obj)

    tmpPath = savePath + os.sep + imgname + '.xml'
    filepath = tmpPath.replace('.xml', '.jpg')
    filename = imgname + '.jpg'
    img2xml_multiobj(tmpPath, tmpPath, folder, filename, filepath, imgshape[1],
                     imgshape[0], objs)

    logger.info('Saved to {}.'.format(tmpPath))

    if flag:
        skimage.io.imsave(filepath, mosiacImg)


def mosiac_img(imgs: list, heightFactor=0.5, widthFactor=0.5):
    if not type(imgs) is list:
        logger.error('Input must be a list!')
        return

    if len(imgs) == 0:
        logger.error('None image found!')
        return

    if len(imgs) == 1:
        for _ in range(0, 3):
            imgs.append(imgs[0])

    if len(imgs) == 2:
        for _ in range(0, 2):
            imgs.append(imgs[0])

    if len(imgs) == 3:
        for _ in range(0, 1):
            imgs.append(imgs[0])

    mHeight, mWidth = getMeanSize(imgs)

    img_left_top = resize_img(
        np.array(skimage.transform.resize(imgs[0], (mHeight, mWidth)) *
                 255).astype(np.uint8), heightFactor, widthFactor)

    img_right_top = resize_img(
        np.array(skimage.transform.resize(imgs[1], (mHeight, mWidth)) *
                 255).astype(np.uint8), heightFactor, 1 - widthFactor)

    img_left_bottom = resize_img(
        np.array(skimage.transform.resize(imgs[2], (mHeight, mWidth)) *
                 255).astype(np.uint8), 1 - heightFactor, widthFactor)

    img_right_bottom = resize_img(
        np.array(skimage.transform.resize(imgs[3], (mHeight, mWidth)) *
                 255).astype(np.uint8), 1 - heightFactor, 1 - widthFactor)

    h1 = np.hstack((img_left_top, img_right_top))
    h2 = np.hstack((img_left_bottom, img_right_bottom))

    return np.vstack((h1, h2))


def mosiac_img_no_reshape(imgs: list, heightFactor=0.5, widthFactor=0.5):
    assert type(imgs) is list and len(
        imgs) == 4, "input must be a list[str_or_ndarray] with length=4"

    img1, img2, img3, img4 = imgs[0], imgs[1], imgs[2], imgs[3]

    if isinstance(img1, str):
        img1 = io.imread(img1)

    if isinstance(img2, str):
        img2 = io.imread(img2)

    if isinstance(img3, str):
        img3 = io.imread(img3)

    if isinstance(img4, str):
        img4 = io.imread(img4)

    imgShape1 = img1.shape
    img2 = cv2.resize(img2, (imgShape1[1], imgShape1[0]),
                      interpolation=cv2.INTER_CUBIC)
    img3 = cv2.resize(img3, (imgShape1[1], imgShape1[0]),
                      interpolation=cv2.INTER_CUBIC)
    img4 = cv2.resize(img4, (imgShape1[1], imgShape1[0]),
                      interpolation=cv2.INTER_CUBIC)

    # print(np.max(img1))
    # print(np.max(img2))

    if heightFactor < 0.5:
        heightFactor = 1 - heightFactor

    if widthFactor < 0.5:
        widthFactor = 1 - widthFactor

    # if heightFactor < 0.5:
    #     maskImg = np.zeros((int(imgShape1[0] / (1 - heightFactor)),
    #                         int(imgShape1[1] / (1 - widthFactor)), 3))
    # else:
    maskImg = np.zeros(
        (int(imgShape1[0] / heightFactor), int(imgShape1[1] / widthFactor), 3))

    front = random.randint(0, 4)
    maskShape = maskImg.shape
    # print(maskShape)

    if front == 0:
        maskImg[0:imgShape1[0], maskShape[1] - imgShape1[1]:] = img2
        maskImg[maskShape[0] - imgShape1[0]:, 0:imgShape1[1]] = img3
        maskImg[maskShape[0] - imgShape1[0]:,
                maskShape[1] - imgShape1[1]:] = img4
        maskImg[0:imgShape1[0], 0:imgShape1[1]] = img1

    if front == 1:
        maskImg[maskShape[0] - imgShape1[0]:, 0:imgShape1[1]] = img3
        maskImg[maskShape[0] - imgShape1[0]:,
                maskShape[1] - imgShape1[1]:] = img4
        maskImg[0:imgShape1[0], 0:imgShape1[1]] = img1
        maskImg[0:imgShape1[0], maskShape[1] - imgShape1[1]:] = img2

    if front == 2:
        maskImg[maskShape[0] - imgShape1[0]:,
                maskShape[1] - imgShape1[1]:] = img4
        maskImg[0:imgShape1[0], 0:imgShape1[1]] = img1
        maskImg[0:imgShape1[0], maskShape[1] - imgShape1[1]:] = img2
        maskImg[maskShape[0] - imgShape1[0]:, 0:imgShape1[1]] = img3

    if front == 3:
        maskImg[0:imgShape1[0], 0:imgShape1[1]] = img1
        maskImg[0:imgShape1[0], maskShape[1] - imgShape1[1]:] = img2
        maskImg[maskShape[0] - imgShape1[0]:, 0:imgShape1[1]] = img3
        maskImg[maskShape[0] - imgShape1[0]:,
                maskShape[1] - imgShape1[1]:] = img4

    # print(np.max(maskImg))
    return maskImg.astype(np.uint8), front


def mosiacScript_no_reshape(imgs: list, xmls: list, savePath: str, flag=False):
    heightFactor = random.uniform(0.1, 0.5)
    widthFactor = random.uniform(0.1, 0.5)

    img1, img2, img3, img4 = imgs[0], imgs[1], imgs[2], imgs[3]

    if not type(imgs) is list or not type(xmls) is list:
        logger.error('Input must be list!')
        return

    imgname = getName(xmls)
    folder = savePath
    mosiacImg, front = mosiac_img_no_reshape(imgs, heightFactor, widthFactor)

    tree1 = ET.parse(xmls[0])
    tree2 = resizeScript(img2,
                         xmls[1],
                         heightFactor=img1.shape[0] / img2.shape[0],
                         widthFactor=img1.shape[1] / img2.shape[1],
                         flag=False)
    
    tree3 = resizeScript(img3,
                         xmls[2],
                         heightFactor=img1.shape[0] / img3.shape[0],
                         widthFactor=img1.shape[1] / img3.shape[1],
                         flag=False)

    tree4 = resizeScript(img4,
                         xmls[3],
                         heightFactor=img1.shape[0] / img4.shape[0],
                         widthFactor=img1.shape[1] / img4.shape[1],
                         flag=False)
    
    root2 = tree2.getroot()
    for o in root2.iter():
        pass
    
    if front == 0:
        pass

    if front == 1:
        pass

    if front == 2:
        pass

    if front == 3:
        pass
