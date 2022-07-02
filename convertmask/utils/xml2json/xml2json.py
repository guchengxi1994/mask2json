'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-09-24 09:03:04
LastEditors: xiaoshuyui
LastEditTime: 2021-02-19 16:40:13
'''
import json
import os
import traceback
try:
    import defusedxml.ElementTree as ET
except:
    import xml.etree.ElementTree as ET

from convertmask.utils.methods.img2base64 import imgEncode
from convertmask.utils.methods.logger import logger
from skimage import io

# import numpy as np
# import cv2
try:
    from labelme import __version__ as labelmeVersion
except:
    labelmeVersion = '4.2.9'


def x2jConvert(xmlpath, originImgPath, flag=True):
    """this function is used to convert xml files (labelimg) to jsons (labelme)

    """
    if not os.path.exists(xmlpath) or not os.path.exists(originImgPath):
        logger.error('file not exist')
        return

    base64Code = imgEncode(originImgPath)
    shapes = getPolygon(xmlpath)

    (fatherPath, filename_ext) = os.path.split(originImgPath)
    (filename, _) = os.path.splitext(filename_ext)

    ob = dict()
    ob['imageData'] = base64Code
    ob['flags'] = {}
    ob['version'] = labelmeVersion
    ob['imagePath'] = filename_ext

    img = io.imread(originImgPath)
    imgShape = img.shape
    del img
    ob['imageHeight'] = imgShape[0]
    ob['imageWidth'] = imgShape[1]
    ob['shapes'] = shapes

    if flag:
        with open(fatherPath + os.sep + filename + '.json',
                  'w',
                  encoding='utf-8') as f:
            j = json.dumps(ob, sort_keys=True, indent=4)
            f.write(j)

        logger.info('save to path {}'.format(fatherPath + os.sep + filename +
                                             '.json'))
        return fatherPath + os.sep + filename + '.json'
    else:
        return json.dumps(ob, sort_keys=True, indent=4)


def x2jConvert_pascal(xmlpath, originImgPath, flag=True):
    # pass
    if not os.path.exists(xmlpath) or not os.path.exists(originImgPath):
        logger.error('file not exist')
        return

    base64Code = imgEncode(originImgPath)
    shapes = getPolygonPascal(xmlpath)

    (fatherPath, filename_ext) = os.path.split(originImgPath)
    (filename, _) = os.path.splitext(filename_ext)

    ob = dict()
    ob['imageData'] = base64Code
    ob['flags'] = {}
    ob['version'] = labelmeVersion
    ob['imagePath'] = filename_ext

    img = io.imread(originImgPath)
    imgShape = img.shape
    del img
    ob['imageHeight'] = imgShape[0]
    ob['imageWidth'] = imgShape[1]
    ob['shapes'] = shapes

    if flag:
        with open(fatherPath + os.sep + filename + '_p.json',
                  'w',
                  encoding='utf-8') as f:
            j = json.dumps(ob, sort_keys=True, indent=4)
            f.write(j)

        logger.info('save to path {}'.format(fatherPath + os.sep + filename +
                                             '_p.json'))
        return fatherPath + os.sep + filename + '_p.json'
    else:
        return json.dumps(ob, sort_keys=True, indent=4)


def getImgShape(xmlPath):
    in_file = open(xmlPath)
    tree = ET.parse(in_file)
    root = tree.getroot()

    imgSize = root.find('size')
    imgwidth = imgSize.find('width').text
    imgheight = imgSize.find('height').text

    return imgwidth, imgheight


def getPolygon(xmlPath):
    in_file = open(xmlPath)
    tree = ET.parse(in_file)
    root = tree.getroot()
    shapes = []
    try:
        for obj in root.iter('object'):
            flags = {}
            group_id = 'null'
            shape_type = 'polygon'
            # pass

            dic = dict()
            label = obj.find('name').text
            polygon = obj.find('polygon')
            # print(len(polygon))
            if len(polygon) > 2:
                points = []
                for i in range(0, len(polygon)):
                    # print(polygon.find('point{}'.format(i)).text)
                    tmp = polygon.find('point{}'.format(i)).text.split(',')
                    point = [int(tmp[0]), int(tmp[1])]
                    # print(point)
                    points.append(point)

                    del tmp, point

                    dic['flags'] = flags
                    dic['group_id'] = group_id
                    dic['shape_type'] = shape_type
                    dic['points'] = points
                    dic['label'] = label
            shapes.append(dic)
        # print(shapes)
        return shapes
    except Exception:
        logger.error(traceback.print_exc())


def getPolygonPascal(xmlPath):
    in_file = open(xmlPath)
    tree = ET.parse(in_file)
    root = tree.getroot()
    shapes = []
    try:
        for obj in root.iter('object'):
            flags = {}
            group_id = 'null'
            shape_type = 'polygon'
            # pass

            dic = dict()
            label = obj.find('name').text
            polygon = obj.find('bndbox')
            # print(len(polygon))
            # if len(polygon)>2:
            # points = []
            # for i in range(0,len(polygon)):
            xmin = int(polygon.find('xmin').text)
            ymin = int(polygon.find('ymin').text)
            xmax = int(polygon.find('xmax').text)
            ymax = int(polygon.find('ymax').text)
            # print(polygon.find('point{}'.format(i)).text)
            # tmp = polygon.find('point{}'.format(i)).text.split(',')
            # point = [int(tmp[0]),int(tmp[1])]
            # print(point)
            p1 = [xmin, ymin]
            p2 = [xmax, ymax]
            p3 = [xmin, ymax]
            p4 = [xmax, ymin]
            # points.append(point)
            points = [p1, p2, p3, p4]
            # del tmp,point

            dic['flags'] = flags
            dic['group_id'] = group_id
            dic['shape_type'] = shape_type
            dic['points'] = points
            dic['label'] = label
            shapes.append(dic)
        # print(shapes)
        return shapes
    except Exception:
        logger.error(traceback.print_exc())
