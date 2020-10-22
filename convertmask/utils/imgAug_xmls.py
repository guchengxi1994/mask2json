'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-10-21 19:10:40
LastEditors: xiaoshuyui
LastEditTime: 2020-10-22 13:34:11
'''
from convertmask.utils.methods.logger import logger
from convertmask.utils.imgAug_nolabel import imgFlip, imgNoise, imgRotation, imgTranslation, imgZoom
import xml.etree.ElementTree as ET
import cv2
import math
import numpy as np
import os
from skimage import io
import shutil
from convertmask.utils.methods.entity import Ori_Pro
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

    rotatedImg.processedImg = label
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


def translation():
    pass


def zoom():
    pass


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

    l[l != 1] = 1

    l = l.tolist()
    # print(l)

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
    noisedImg = noise(img, labelPath)
    rotatedImg = rotate(noisedImg.oriImg, noisedImg.processedImg)

    resXmlPath = parent_path + os.sep + 'augxmls_' + os.sep + filename + '_assumbel.xml'
    resImgPath = parent_path + os.sep + 'augxmls_' + os.sep + filename + '_assumbel.jpg'

    tree = ET.parse(labelPath)
    root = tree.getroot()
    root.find('folder').text = str(resImgPath.split(os.sep)[-1] if \
                                resImgPath.split(os.sep)[-1] != "" else resImgPath.split(os.sep)[-2] )
    root.find('filename').text = filename + '_assumbel.jpg'
    root.find('path').text = resImgPath
    tree.write(resXmlPath)

    io.imsave(resImgPath, rotatedImg.oriImg)
