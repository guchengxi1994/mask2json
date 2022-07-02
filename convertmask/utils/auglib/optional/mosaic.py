from convertmask import baseDecorate
import copy
import datetime
import os
import random
try:
    import defusedxml.ElementTree as ET
except:
    import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

import cv2
import numpy as np
import skimage
from convertmask.utils.auglib.optional.resize import resize_img
from convertmask.utils.img2xml.processor_multi_object import img2xml_multiobj
from convertmask.utils.methods.logger import logger
from convertmask.utils.xml2yolo.xml2yolo import convert as x2yVert
from convertmask.utils.yolo2xml.yolo2xml import convert as y2xVert
from skimage import io

from .resize import resizeScript


def getBoxes(front: int, root1: Element, root2: Element, root3: Element,
             root4: Element, imgShape: tuple, heightFactor: float,
             widthFactor: float):
    root1_ = copy.deepcopy(root1)
    root2_ = copy.deepcopy(root2)
    root3_ = copy.deepcopy(root3)
    root4_ = copy.deepcopy(root4)

    if front == 1:
        # 1

        # 2
        for o in root2_.iter('object'):
            box = o.find('bndbox')
            xmin = float(box.find('xmin').text)
            ymin = float(box.find('ymin').text)
            xmax = float(box.find('xmax').text)
            ymax = float(box.find('ymax').text)

            # if ymin >= heightFactor * imgShape[0] or xmax <= imgShape[1] * (
            #         1 - widthFactor):
            if xmax <= imgShape[1] * (1 - widthFactor):
                box.find('xmin').text = str(0)
                box.find('xmax').text = str(0)
                box.find('ymin').text = str(0)
                box.find('ymax').text = str(0)

            else:
                # if ymin < heightFactor * imgShape[0]:
                #     if ymax > heightFactor * imgShape[0]:
                #         box.find('ymax').text = str(int(heightFactor *
                #                                         imgShape[0]))

                if xmax > imgShape[1] * (1 - widthFactor):
                    if xmin < imgShape[1] * (1 - widthFactor):
                        box.find('xmin').text = str(
                            int(imgShape[1] * (1 - widthFactor)))

        # 3
        for o in root3_.iter('object'):
            box = o.find('bndbox')
            xmin = float(box.find('xmin').text)
            ymin = float(box.find('ymin').text)
            xmax = float(box.find('xmax').text)
            ymax = float(box.find('ymax').text)
            # if ymax <= (1-heightFactor) * imgShape[
            #         0] or xmin >= widthFactor * imgShape[1]:
            if ymax <= (1 - heightFactor) * imgShape[0]:
                box.find('xmin').text = str(0)
                box.find('xmax').text = str(0)
                box.find('ymin').text = str(0)
                box.find('ymax').text = str(0)
            else:
                if ymax > imgShape[0] * (1 - heightFactor):
                    if ymin < imgShape[0] * (1 - heightFactor):
                        box.find('ymin').text = str(
                            int(imgShape[0] * (1 - heightFactor)))

                # if xmin < widthFactor * imgShape[1]:
                #     if xmax > widthFactor * imgShape[1]:
                #         box.find('xmax').text = str(int(widthFactor * imgShape[1]))

        # 4
        for o in root4_.iter('object'):
            box = o.find('bndbox')
            xmin = float(box.find('xmin').text)
            ymin = float(box.find('ymin').text)
            xmax = float(box.find('xmax').text)
            ymax = float(box.find('ymax').text)

            if xmax <= imgShape[1] * (1 - widthFactor) or ymax <= imgShape[
                    0] * (1 - heightFactor):
                box.find('xmin').text = str(0)
                box.find('xmax').text = str(0)
                box.find('ymin').text = str(0)
                box.find('ymax').text = str(0)
            else:
                if ymax > imgShape[0] * (1 - heightFactor):
                    if ymin < imgShape[0] * (1 - heightFactor):
                        box.find('ymin').text = str(
                            int(imgShape[0] * (1 - heightFactor)))

                if xmax > imgShape[1] * (1 - widthFactor):
                    if xmin < imgShape[1] * (1 - widthFactor):
                        box.find('xmin').text = str(
                            int(imgShape[1] * (1 - widthFactor)))

    if front == 2:
        # 1
        for o in root1_.iter('object'):
            box = o.find('bndbox')
            xmin = float(box.find('xmin').text)
            ymin = float(box.find('ymin').text)
            xmax = float(box.find('xmax').text)
            ymax = float(box.find('ymax').text)

            if ymin >= (1 - heightFactor
                        ) * imgShape[0] or xmin >= widthFactor * imgShape[1]:

                box.find('xmin').text = str(0)
                box.find('xmax').text = str(0)
                box.find('ymin').text = str(0)
                box.find('ymax').text = str(0)

            else:
                if ymin < (1 - heightFactor) * imgShape[0]:
                    if ymax > (1 - heightFactor) * imgShape[0]:
                        box.find('ymax').text = str(
                            int((1 - heightFactor) * imgShape[0]))

                if xmin < widthFactor * imgShape[1]:
                    if xmax > widthFactor * imgShape[1]:
                        box.find('xmax').text = str(
                            int(widthFactor * imgShape[1]))

        # 2

        # 3
        for o in root3_.iter('object'):
            box = o.find('bndbox')
            xmin = float(box.find('xmin').text)
            ymin = float(box.find('ymin').text)
            xmax = float(box.find('xmax').text)
            ymax = float(box.find('ymax').text)
            # if ymax <= (1-heightFactor) * imgShape[
            #         0] or xmin >= widthFactor * imgShape[1]:
            if ymax <= (1 - heightFactor) * imgShape[0]:
                box.find('xmin').text = str(0)
                box.find('xmax').text = str(0)
                box.find('ymin').text = str(0)
                box.find('ymax').text = str(0)
            else:
                if ymax > imgShape[0] * (1 - heightFactor):
                    if ymin < imgShape[0] * (1 - heightFactor):
                        box.find('ymin').text = str(
                            int(imgShape[0] * (1 - heightFactor)))

                # if xmin < widthFactor * imgShape[1]:
                #     if xmax > widthFactor * imgShape[1]:
                #         box.find('xmax').text = str(int(widthFactor * imgShape[1]))

        # 4
        for o in root4_.iter('object'):
            box = o.find('bndbox')
            xmin = float(box.find('xmin').text)
            ymin = float(box.find('ymin').text)
            xmax = float(box.find('xmax').text)
            ymax = float(box.find('ymax').text)

            if xmax <= imgShape[1] * (1 - widthFactor) or ymax <= imgShape[
                    0] * (1 - heightFactor):
                box.find('xmin').text = str(0)
                box.find('xmax').text = str(0)
                box.find('ymin').text = str(0)
                box.find('ymax').text = str(0)
            else:
                if ymax > imgShape[0] * (1 - heightFactor):
                    if ymin < imgShape[0] * (1 - heightFactor):
                        box.find('ymin').text = str(
                            int(imgShape[0] * (1 - heightFactor)))

                if xmax > imgShape[1] * (1 - widthFactor):
                    if xmin < imgShape[1] * (1 - widthFactor):
                        box.find('xmin').text = str(
                            int(imgShape[1] * (1 - widthFactor)))

    if front == 3:
        # 1
        for o in root1_.iter('object'):
            box = o.find('bndbox')
            xmin = float(box.find('xmin').text)
            ymin = float(box.find('ymin').text)
            xmax = float(box.find('xmax').text)
            ymax = float(box.find('ymax').text)

            if ymin >= heightFactor * imgShape[0] or xmin >= (
                    1 - widthFactor) * imgShape[1]:

                box.find('xmin').text = str(0)
                box.find('xmax').text = str(0)
                box.find('ymin').text = str(0)
                box.find('ymax').text = str(0)

            else:
                if ymin < heightFactor * imgShape[0]:
                    if ymax > heightFactor * imgShape[0]:
                        box.find('ymax').text = str(
                            int(heightFactor * imgShape[0]))

                if xmin < widthFactor * (1 - imgShape[1]):
                    if xmax > widthFactor * (1 - imgShape[1]):
                        box.find('xmax').text = str(
                            int(widthFactor * (1 - imgShape[1])))

        # 2
        for o in root2_.iter('object'):
            box = o.find('bndbox')
            xmin = float(box.find('xmin').text)
            ymin = float(box.find('ymin').text)
            xmax = float(box.find('xmax').text)
            ymax = float(box.find('ymax').text)

            # if ymin >= heightFactor * imgShape[0] or xmax <= imgShape[1] * (
            #         1 - widthFactor):
            if xmax <= imgShape[1] * (1 - widthFactor):
                box.find('xmin').text = str(0)
                box.find('xmax').text = str(0)
                box.find('ymin').text = str(0)
                box.find('ymax').text = str(0)

            else:
                # if ymin < heightFactor * imgShape[0]:
                #     if ymax > heightFactor * imgShape[0]:
                #         box.find('ymax').text = str(int(heightFactor *
                #                                         imgShape[0]))

                if xmax > imgShape[1] * (1 - widthFactor):
                    if xmin < imgShape[1] * (1 - widthFactor):
                        box.find('xmin').text = str(
                            int(imgShape[1] * (1 - widthFactor)))

        # 3

        # 4
        for o in root4_.iter('object'):
            box = o.find('bndbox')
            xmin = float(box.find('xmin').text)
            ymin = float(box.find('ymin').text)
            xmax = float(box.find('xmax').text)
            ymax = float(box.find('ymax').text)

            if xmax <= imgShape[1] * (1 - widthFactor) or ymax <= imgShape[
                    0] * (1 - heightFactor):
                box.find('xmin').text = str(0)
                box.find('xmax').text = str(0)
                box.find('ymin').text = str(0)
                box.find('ymax').text = str(0)
            else:
                if ymax > imgShape[0] * (1 - heightFactor):
                    if ymin < imgShape[0] * (1 - heightFactor):
                        box.find('ymin').text = str(
                            int(imgShape[0] * (1 - heightFactor)))

                if xmax > imgShape[1] * (1 - widthFactor):
                    if xmin < imgShape[1] * (1 - widthFactor):
                        box.find('xmin').text = str(
                            int(imgShape[1] * (1 - widthFactor)))

    if front == 4:
        # 1
        for o in root1_.iter('object'):
            box = o.find('bndbox')
            xmin = float(box.find('xmin').text)
            ymin = float(box.find('ymin').text)
            xmax = float(box.find('xmax').text)
            ymax = float(box.find('ymax').text)

            if ymin >= heightFactor * imgShape[
                    0] or xmin >= widthFactor * imgShape[1]:

                box.find('xmin').text = str(0)
                box.find('xmax').text = str(0)
                box.find('ymin').text = str(0)
                box.find('ymax').text = str(0)

            else:
                if ymin < heightFactor * imgShape[0]:
                    if ymax > heightFactor * imgShape[0]:
                        box.find('ymax').text = str(
                            int(heightFactor * imgShape[0]))

                if xmin < widthFactor * imgShape[1]:
                    if xmax > widthFactor * imgShape[1]:
                        box.find('xmax').text = str(
                            int(widthFactor * imgShape[1]))

        # 2
        for o in root2_.iter('object'):
            box = o.find('bndbox')
            xmin = float(box.find('xmin').text)
            ymin = float(box.find('ymin').text)
            xmax = float(box.find('xmax').text)
            ymax = float(box.find('ymax').text)

            # if ymin >= heightFactor * imgShape[0] or xmax <= imgShape[1] * (
            #         1 - widthFactor):
            if xmax <= imgShape[
                    1] * widthFactor or ymin >= heightFactor * imgShape[0]:
                box.find('xmin').text = str(0)
                box.find('xmax').text = str(0)
                box.find('ymin').text = str(0)
                box.find('ymax').text = str(0)

            else:
                if ymin < heightFactor * imgShape[0]:
                    if ymax > heightFactor * imgShape[0]:
                        box.find('ymax').text = str(
                            int(heightFactor * imgShape[0]))

                if xmax > imgShape[1] * widthFactor:
                    if xmin < imgShape[1] * widthFactor:
                        box.find('xmin').text = str(
                            int(imgShape[1] * widthFactor))

        # 3
        for o in root3_.iter('object'):
            box = o.find('bndbox')
            xmin = float(box.find('xmin').text)
            ymin = float(box.find('ymin').text)
            xmax = float(box.find('xmax').text)
            ymax = float(box.find('ymax').text)
            # if ymax <= (1-heightFactor) * imgShape[
            #         0] or xmin >= widthFactor * imgShape[1]:
            if ymax <= heightFactor * imgShape[
                    0] or xmin >= widthFactor * imgShape[1]:
                box.find('xmin').text = str(0)
                box.find('xmax').text = str(0)
                box.find('ymin').text = str(0)
                box.find('ymax').text = str(0)
            else:
                if ymax > imgShape[0] * heightFactor:
                    if ymin < imgShape[0] * heightFactor:
                        box.find('ymin').text = str(
                            int(imgShape[0] * heightFactor))

                if xmin < widthFactor * imgShape[1]:
                    if xmax > widthFactor * imgShape[1]:
                        box.find('xmax').text = str(
                            int(widthFactor * imgShape[1]))

        # 4

    return root1_, root2_, root3_, root4_


def getMeanSize(imgs: list):
    height = []
    width = []
    for i in imgs:
        height.append(i.shape[0])
        width.append(i.shape[1])

    return int(np.mean(height)), int(np.mean(width))


def getName(xmls: list):
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

@baseDecorate()
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

    if heightFactor < 0.5:
        heightFactor = 1 - heightFactor

    if widthFactor < 0.5:
        widthFactor = 1 - widthFactor

    maskImg = np.zeros(
        (int(imgShape1[0] / heightFactor), int(imgShape1[1] / widthFactor), 3))

    front = random.randint(0, 3)

    maskShape = maskImg.shape
    res = []

    if front == 0:
        maskImg[maskShape[0] - imgShape1[0]:,
                maskShape[1] - imgShape1[1]:] = img4
        maskImg[0:imgShape1[0], maskShape[1] - imgShape1[1]:] = img2
        maskImg[maskShape[0] - imgShape1[0]:, 0:imgShape1[1]] = img3
        maskImg[0:imgShape1[0], 0:imgShape1[1]] = img1
        res = [1, 4, 2, 3]

    if front == 1:
        maskImg[maskShape[0] - imgShape1[0]:,
                maskShape[1] - imgShape1[1]:] = img4
        maskImg[maskShape[0] - imgShape1[0]:, 0:imgShape1[1]] = img3
        maskImg[0:imgShape1[0], 0:imgShape1[1]] = img1
        maskImg[0:imgShape1[0], maskShape[1] - imgShape1[1]:] = img2
        res = [2, 4, 3, 1]

    if front == 2:
        maskImg[maskShape[0] - imgShape1[0]:,
                maskShape[1] - imgShape1[1]:] = img4
        maskImg[0:imgShape1[0], maskShape[1] - imgShape1[1]:] = img2
        maskImg[0:imgShape1[0], 0:imgShape1[1]] = img1
        maskImg[maskShape[0] - imgShape1[0]:, 0:imgShape1[1]] = img3
        res = [3, 4, 2, 1]

    if front == 3:
        maskImg[0:imgShape1[0], 0:imgShape1[1]] = img1
        maskImg[0:imgShape1[0], maskShape[1] - imgShape1[1]:] = img2
        maskImg[maskShape[0] - imgShape1[0]:, 0:imgShape1[1]] = img3
        maskImg[maskShape[0] - imgShape1[0]:,
                maskShape[1] - imgShape1[1]:] = img4
        res = [4, 1, 2, 3]

    return maskImg.astype(np.uint8), res, heightFactor, widthFactor


def mosiacScript_no_reshape(imgs: list, xmls: list, savePath: str, flag=False):
    heightFactor = random.uniform(0.1, 0.5)
    widthFactor = random.uniform(0.1, 0.5)

    img1, img2, img3, img4 = imgs[0], imgs[1], imgs[2], imgs[3]

    if not type(imgs) is list or not type(xmls) is list:
        logger.error('Input must be list!')
        return

    imgname = getName(xmls)
    folder = savePath
    mosiacImg, res, _, _ = mosiac_img_no_reshape(imgs, heightFactor,
                                                 widthFactor)
    front = res[0]

    heightFactor = min(heightFactor, 1 - heightFactor)
    widthFactor = min(widthFactor, 1 - widthFactor)

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

    root1 = tree1.getroot()
    root2 = tree2.getroot()
    for box in root2.iter('bndbox'):
        xmin = float(box.find('xmin').text)
        ymin = float(box.find('ymin').text)
        xmax = float(box.find('xmax').text)
        ymax = float(box.find('ymax').text)
        box.find('xmin').text = str(
            int(xmin + widthFactor * mosiacImg.shape[1]))
        box.find('xmax').text = str(
            int(xmax + widthFactor * mosiacImg.shape[1]))

    root3 = tree3.getroot()
    for box in root3.iter('bndbox'):
        xmin = float(box.find('xmin').text)
        ymin = float(box.find('ymin').text)
        xmax = float(box.find('xmax').text)
        ymax = float(box.find('ymax').text)
        box.find('ymin').text = str(
            int(ymin + heightFactor * mosiacImg.shape[0]))
        box.find('ymax').text = str(
            int(ymax + heightFactor * mosiacImg.shape[0]))

    root4 = tree4.getroot()
    for box in root4.iter('bndbox'):
        xmin = float(box.find('xmin').text)
        ymin = float(box.find('ymin').text)
        xmax = float(box.find('xmax').text)
        ymax = float(box.find('ymax').text)
        box.find('xmin').text = str(
            int(xmin + widthFactor * mosiacImg.shape[1]))
        box.find('xmax').text = str(
            int(xmax + widthFactor * mosiacImg.shape[1]))
        box.find('ymin').text = str(
            int(ymin + heightFactor * mosiacImg.shape[0]))
        box.find('ymax').text = str(
            int(ymax + heightFactor * mosiacImg.shape[0]))
    boxes = []

    r1, r2, r3, r4 = getBoxes(front,
                              root1,
                              root2,
                              root3,
                              root4,
                              mosiacImg.shape,
                              heightFactor=heightFactor,
                              widthFactor=widthFactor)

    for box in r1.iter('object'):
        boxes.append(box)

    for box in r2.iter('object'):
        boxes.append(box)

    for box in r3.iter('object'):
        boxes.append(box)

    for box in r4.iter('object'):
        boxes.append(box)
    # print(len(boxes))
    imgshape = mosiacImg.shape
    objs = []
    for o in boxes:
        obj = dict()
        name = o.find('name').text
        difficult = 0
        xmlbox = o.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text),
             float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
        tmp = dict()
        tmp['xmin'] = str(int(b[0]))
        tmp['ymin'] = str(int(b[2]))
        tmp['xmax'] = str(int(b[1]))
        tmp['ymax'] = str(int(b[3]))
        # print(tmp)
        if not (int(tmp['xmin']) == 0 and int(tmp['xmax']) == 0
                and int(tmp['ymin']) == 0 and int(tmp['ymax']) == 0):
            obj['name'] = name
            obj['difficult'] = difficult
            obj['bndbox'] = tmp
            objs.append(obj)
        del tmp
    # print(len(objs))
    tmpPath = savePath + os.sep + imgname + '.xml'
    filepath = tmpPath.replace('.xml', '.jpg')
    filename = imgname + '.jpg'
    img2xml_multiobj(tmpPath, tmpPath, folder, filename, filepath, imgshape[1],
                     imgshape[0], objs)

    logger.info('Saved to {}.'.format(tmpPath))

    if flag:
        skimage.io.imsave(filepath, mosiacImg)
