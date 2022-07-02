'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-10-21 19:10:40
LastEditors: xiaoshuyui
LastEditTime: 2021-02-19 17:04:45
'''
import math
import os
import random
import shutil
try:
    import defusedxml.ElementTree as ET
except:
    import xml.etree.ElementTree as ET

import cv2
import numpy as np
from convertmask.utils.auglib.img_aug_nolabel import imgNoise
# from convertmask.utils.methods.entity import Ori_Pro
from convertmask import Ori_Pro
from convertmask.utils.methods.logger import logger
from skimage import io

"""
if flag == True, then images and xmls will be saved. Better just for test.
"""


def flip_img(src, flipType=0):
    return cv2.flip(src, flipType)


def flip_xml(src, xmin, ymin, xmax, ymax, flipType=0):
    """
    src : src image
    flipType: 0 or 1(>0) or -1(<0)
    """
    w = src.shape[1]
    h = src.shape[0]

    if flipType == 0:
        return xmin, h - ymax, xmax, h - ymin
    elif flipType == 1:
        return w - xmax, ymin, w - xmin, ymax
    else:
        return w - xmax, h - ymax, w - xmin, h - ymin


def rotate_image(src, angle, scale=1.):
    w = src.shape[1]
    h = src.shape[0]
    # convet angle into rad
    rangle = np.deg2rad(angle)  # angle in radians
    # calculate new image width and height
    nw = (abs(np.sin(rangle) * h) + abs(np.cos(rangle) * w)) * scale
    nh = (abs(np.cos(rangle) * h) + abs(np.sin(rangle) * w)) * scale
    # ask OpenCV for the rotation matrix
    rot_mat = cv2.getRotationMatrix2D((nw * 0.5, nh * 0.5), angle, scale)
    # calculate the move from the old center to the new center combined
    # with the rotation
    rot_move = np.dot(rot_mat, np.array([(nw - w) * 0.5, (nh - h) * 0.5, 0]))
    # the move only affects the translation, so update the translation
    # part of the transform
    rot_mat[0, 2] += rot_move[0]
    rot_mat[1, 2] += rot_move[1]
    # map
    return cv2.warpAffine(src,
                          rot_mat, (int(math.ceil(nw)), int(math.ceil(nh))),
                          flags=cv2.INTER_LANCZOS4)


def rotate_xml(src, xmin, ymin, xmax, ymax, angle, scale=1.):
    w = src.shape[1]
    h = src.shape[0]
    rangle = np.deg2rad(angle)  # angle in radians
    # now calculate new image width and height
    # get width and heigh of changed image
    nw = (abs(np.sin(rangle) * h) + abs(np.cos(rangle) * w)) * scale
    nh = (abs(np.cos(rangle) * h) + abs(np.sin(rangle) * w)) * scale
    # ask OpenCV for the rotation matrix
    rot_mat = cv2.getRotationMatrix2D((nw * 0.5, nh * 0.5), angle, scale)
    # calculate the move from the old center to the new center combined
    # with the rotation
    rot_move = np.dot(rot_mat, np.array([(nw - w) * 0.5, (nh - h) * 0.5, 0]))
    # the move only affects the translation, so update the translation
    # part of the transform
    rot_mat[0, 2] += rot_move[0]
    rot_mat[1, 2] += rot_move[1]
    # rot_mat: the final rot matrix
    # get the four center of edges in the initial martix，and convert the coord
    point1 = np.dot(rot_mat, np.array([(xmin + xmax) / 2, ymin, 1]))
    point2 = np.dot(rot_mat, np.array([xmax, (ymin + ymax) / 2, 1]))
    point3 = np.dot(rot_mat, np.array([(xmin + xmax) / 2, ymax, 1]))
    point4 = np.dot(rot_mat, np.array([xmin, (ymin + ymax) / 2, 1]))
    # concat np.array
    concat = np.vstack((point1, point2, point3, point4))
    # change type
    concat = concat.astype(np.int32)
    # print(concat)
    rx, ry, rw, rh = cv2.boundingRect(concat)
    return rx, ry, rw, rh


def trans_xml(src, xmin, ymin, xmax, ymax, th, tv):
    w = src.shape[1]  # width
    h = src.shape[0]  # height

    xmin = xmin + tv
    xmax = xmax + tv if xmax + tv <= w else w
    ymin = ymin + th
    ymax = ymax + th if ymax + th <= h else h

    return xmin, xmax, ymin, ymax


def trans_img(src, th, tv):
    w = src.shape[1]  # width
    h = src.shape[0]  # height
    return cv2.copyMakeBorder(src, th, 0, tv, 0, cv2.BORDER_CONSTANT)[0:h, 0:w]


def zoom_img(src, zoomfactor):
    oriImgShape = src.shape
    w = oriImgShape[1]  # width
    h = oriImgShape[0]  # height

    resW = int(w * zoomfactor)
    resH = int(h * zoomfactor)

    zoomImg = cv2.resize(src, (resW, resH), cv2.INTER_AREA)
    zoomImgShape = zoomImg.shape
    if zoomfactor > 1:
        vDis = zoomImgShape[0] - oriImgShape[0]
        hDis = zoomImgShape[1] - oriImgShape[1]
        vDisHalf = int(vDis * 0.5)
        hDisHalf = int(hDis * 0.5)
        res = zoomImg[vDisHalf:zoomImgShape[0] + vDisHalf - vDis,
                      hDisHalf:zoomImgShape[1] + hDisHalf - hDis]
    elif zoomfactor < 1:
        vDis = abs(zoomImgShape[0] - oriImgShape[0])
        hDis = abs(zoomImgShape[1] - oriImgShape[1])
        vDisHalf = int(vDis * 0.5)
        hDisHalf = int(hDis * 0.5)

        res = cv2.copyMakeBorder(
            zoomImg,
            vDisHalf,
            vDis - vDisHalf,
            hDisHalf,
            hDis - hDisHalf,
            cv2.BORDER_CONSTANT,
        )
    else:
        logger.warning('zoomfactor is 1')
        res = src
    return res


def zoom_xml(src, zoomfactor, xmin, ymin, xmax, ymax):
    # print(zoomfactor)
    oriImgShape = src.shape
    if zoomfactor < 1:
        vDis = 0.5 * (oriImgShape[0] - oriImgShape[0] * zoomfactor)
        hDis = 0.5 * (oriImgShape[1] - oriImgShape[1] * zoomfactor)
        resYmin = zoomfactor * ymin + vDis
        resYmax = zoomfactor * ymax + vDis
        resXmin = zoomfactor * xmin + hDis
        resXmax = zoomfactor * xmax + hDis
    else:
        vDis = abs(0.5 * (oriImgShape[0] - oriImgShape[0] * zoomfactor))
        hDis = abs(0.5 * (oriImgShape[1] - oriImgShape[1] * zoomfactor))

        resYmin = zoomfactor * ymin - vDis
        resYmax = zoomfactor * ymax - vDis
        resXmin = zoomfactor * xmin - hDis
        resXmax = zoomfactor * xmax - hDis

    return resXmin, resXmax, resYmin, resYmax


def rotate(oriImg: np.ndarray, label: str, angle=10, scale=1, flag=False):
    # rotatedImg = imgRotation(oriImg, angle, scale, flag=flag)['rotation']
    rotated = rotate_image(oriImg, angle, scale)
    tree = ET.parse(label)
    root = tree.getroot()
    for box in root.iter('bndbox'):
        xmin = float(box.find('xmin').text)
        ymin = float(box.find('ymin').text)
        xmax = float(box.find('xmax').text)
        ymax = float(box.find('ymax').text)
        x, y, w, h = rotate_xml(oriImg, xmin, ymin, xmax, ymax, angle, scale)
        box.find('xmin').text = str(x)
        box.find('ymin').text = str(y)
        box.find('xmax').text = str(x + w)
        box.find('ymax').text = str(y + h)
        box.set('updated', 'yes')
    tree.write(label)

    rotatedImg = Ori_Pro(rotated, label)
    return rotatedImg


def flip(oriImg: np.ndarray, label: str, flag=False):
    flipParams = [-1, 0, 1]
    flipRes = []
    filepath, ext = os.path.splitext(label)
    for i in range(0, len(flipParams)):
        img = flip_img(oriImg, flipParams[i])
        xmlpath = filepath + '_' + str(i) + ext
        shutil.copyfile(label, xmlpath)

        tree = ET.parse(xmlpath)
        root = tree.getroot()

        for box in root.iter('bndbox'):
            xmin = float(box.find('xmin').text)
            ymin = float(box.find('ymin').text)
            xmax = float(box.find('xmax').text)
            ymax = float(box.find('ymax').text)
            xmin, ymin, xmax, ymax = flip_xml(img, xmin, ymin, xmax, ymax,
                                              flipParams[i])
            # change the coord
            box.find('xmin').text = str(int(xmin))
            box.find('ymin').text = str(int(ymin))
            box.find('xmax').text = str(int(xmax))
            box.find('ymax').text = str(int(ymax))
            box.set('updated', 'yes')
            # write into new xml
            tree.write(xmlpath)

        flipRes.append(Ori_Pro(img, xmlpath))
    return flipRes


def noise(oriImg: np.ndarray, label: str, flag=False):
    """
    label should be a xml path. a cache file will be generated first.
    """
    noisedImg = imgNoise(oriImg, flag=flag)['noise']
    noisedImg.processedImg = label
    return noisedImg


def translation(oriImg: np.ndarray, label: str, flag=False, factor=0.3):
    th = random.randint(0, int(factor * oriImg.shape[1]))
    tv = random.randint(0, int(factor * oriImg.shape[0]))
    # transImg = imgTranslation(oriImg,flag=False,th=th,tv=tv)['trans']
    transed = trans_img(oriImg, th, tv)
    # print(transed.shape)
    tree = ET.parse(label)
    root = tree.getroot()
    for box in root.iter('bndbox'):
        xmin = float(box.find('xmin').text)
        ymin = float(box.find('ymin').text)
        xmax = float(box.find('xmax').text)
        ymax = float(box.find('ymax').text)
        xmin, xmax, ymin, ymax = trans_xml(oriImg, xmin, ymin, xmax, ymax, th,
                                           tv)
        box.find('xmin').text = str(xmin)
        box.find('ymin').text = str(ymin)
        box.find('xmax').text = str(xmax)
        box.find('ymax').text = str(ymax)
        box.set('updated', 'yes')
    tree.write(label)

    transImg = Ori_Pro(transed, label)
    return transImg


# maybe do it like cv2.imresize
def zoom(oriImg: np.ndarray, label: str, flag=False, zoomfactor=0):
    if zoomfactor <= 0 or zoomfactor == 1:
        zoomfactor = random.uniform(0.8, 1.8)
        zoomfactor = round(zoomfactor, 2)

    zoomed = zoom_img(oriImg, zoomfactor)
    tree = ET.parse(label)
    root = tree.getroot()
    for box in root.iter('bndbox'):
        xmin = float(box.find('xmin').text)
        ymin = float(box.find('ymin').text)
        xmax = float(box.find('xmax').text)
        ymax = float(box.find('ymax').text)
        xmin, xmax, ymin, ymax = zoom_xml(oriImg, zoomfactor, xmin, ymin, xmax,
                                          ymax)
        box.find('xmin').text = str(xmin)
        box.find('ymin').text = str(ymin)
        box.find('xmax').text = str(xmax)
        box.find('ymax').text = str(ymax)
        box.set('updated', 'yes')
    tree.write(label)

    zoomedImg = Ori_Pro(zoomed, label)
    return zoomedImg


def aug_labelimg(filepath, xmlpath, augs=None, num=0):
    default_augs = ['noise', 'rotation', 'trans', 'flip', 'zoom']
    if augs is None:
        augs = ['noise', 'rotation', 'trans', 'flip', 'zoom']
    else:
        if not isinstance(augs, list):
            try:
                augs = list(str(augs))
            except:
                raise ValueError(
                    "parameter:aug's type is wrong. expect a string or list,got {}"
                    .format(str(type(augs))))

        augs = list(set(augs).intersection(set(default_augs)))
        if len(augs) > 0 and augs is not None:
            pass
        else:
            logger.warning(
                'augumentation method is not supported.using default augumentation method.'
            )
            augs = ['noise', 'rotation', 'trans', 'flip', 'zoom']

    if 'flip' in augs:
        augs.remove('flip')
        augs.append('flip')

    l = np.random.randint(2, size=len(augs))

    if np.sum(l) == 0:
        l[0] = 1

    # l[l != 1] = 1    ## For test

    l = l.tolist()

    p = list(zip(augs, l))

    parent_path, file_name = os.path.split(filepath)
    filename, ext = os.path.splitext(file_name)

    if not os.path.exists(parent_path + os.sep + 'tmps_'):
        os.mkdir(parent_path + os.sep + 'tmps_')

    if not os.path.exists(parent_path + os.sep + 'augxmls_'):
        os.mkdir(parent_path + os.sep + 'augxmls_')

    labelPath = parent_path + os.sep + 'tmps_' + os.sep + filename + '_tmps.xml'
    shutil.copyfile(xmlpath, labelPath)
    img = io.imread(filepath)

    for i in p:
        if i[1] == 1:
            # if i[0] == 'test':
            #     pass
            if i[0] == 'rotation':
                angle = random.randint(-10, 10)
                r = rotate(img, labelPath, angle)
                img, labelPath = r.oriImg, r.processedImg
                del r

            elif i[0] == 'trans':
                t = translation(img, labelPath)
                img, labelPath = t.oriImg, t.processedImg
                del t

            elif i[0] == 'zoom':
                z = zoom(img, labelPath)
                img, labelPath = z.oriImg, z.processedImg
                del z

            elif i[0] == 'noise':
                n = noise(img, labelPath)
                img, labelPath = n.oriImg, n.processedImg
                del n

            elif i[0] == 'flip':
                f = flip(img, labelPath)
                # img,labelPath =
                img = []
                labelPath = []
                for i in f:
                    img.append(i.oriImg)
                    labelPath.append(i.processedImg)
                del f

    if not isinstance(img, list):
        resXmlPath = parent_path + os.sep + 'augxmls_' + os.sep + filename + '_assumbel.xml'
        resImgPath = parent_path + os.sep + 'augxmls_' + os.sep + filename + '_assumbel.jpg'

        tree = ET.parse(labelPath)
        root = tree.getroot()
        root.find('folder').text = str(resImgPath.split(os.sep)[-1] if \
                                    resImgPath.split(os.sep)[-1] != "" else resImgPath.split(os.sep)[-2] )
        root.find('filename').text = filename + '_assumbel.jpg'
        root.find('path').text = resImgPath
        tree.write(resXmlPath)

        io.imsave(resImgPath, img)
    else:
        for i in range(0, len(img)):
            resXmlPath = parent_path + os.sep + 'augxmls_' + os.sep + filename + '_assumbel_{}.xml'.format(
                i)
            resImgPath = parent_path + os.sep + 'augxmls_' + os.sep + filename + '_assumbel_{}.jpg'.format(
                i)

            tree = ET.parse(labelPath[i])
            root = tree.getroot()
            root.find('folder').text = str(resImgPath.split(os.sep)[-1] if \
                                        resImgPath.split(os.sep)[-1] != "" else resImgPath.split(os.sep)[-2] )
            root.find(
                'filename').text = filename + '_assumbel_{}.jpg'.format(i)
            root.find('path').text = resImgPath
            tree.write(resXmlPath)

            io.imsave(resImgPath, img[i])

    logger.info('Done! See {}.'.format(parent_path + os.sep + 'augxmls_'))
