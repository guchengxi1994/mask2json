'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-08-19 11:27:38
LastEditors: xiaoshuyui
LastEditTime: 2021-02-19 16:48:43
'''
import json
import os

import numpy as np
from convertmask.utils.img2xml.processor_multi_object import img2xml_multiobj
from convertmask.utils.methods.logger import logger


def j2xConvert(jsonFilePath: str):
    """this function is used to convert jsons(labelme) to xmls(labelImg)

    """
    with open(jsonFilePath, 'r', encoding='utf-8') as f:
        jsonObj = json.load(f)
        if isinstance(jsonObj, str):
            jsonObj = json.loads(jsonObj)

    tmpPath = jsonFilePath.replace('.json', '.xml')
    aimPath = tmpPath
    folder = os.path.abspath(jsonFilePath)

    filename = jsonObj['imagePath']
    path = tmpPath

    width = jsonObj['imageWidth']
    height = jsonObj['imageHeight']

    objs = []

    shapes = jsonObj['shapes']
    # print(type(shapes))
    for shape in shapes:
        label = shape['label']
        points = shape['points']
        # print(type(points))
        tmp = np.array(points)

        # print(tmp)
        obj = dict()
        obj['name'] = label
        obj['difficult'] = 0
        bndbox = dict()
        bndbox['xmin'] = np.min(tmp[:, 0]) if np.min(tmp[:, 0])>0 else 1  # https://github.com/AlexeyAB/darknet  the bounding box cannot be 0
        bndbox['xmax'] = np.max(tmp[:, 0])
        bndbox['ymin'] = np.min(tmp[:, 1]) if np.min(tmp[:, 1])>0 else 1  
        bndbox['ymax'] = np.max(tmp[:, 1])

        obj['bndbox'] = bndbox

        if bndbox['ymax'] - bndbox['ymin'] < 10 or bndbox['xmax'] - bndbox[
                'xmin'] < 10:
            pass
        else:
            objs.append(obj)

    img2xml_multiobj(tmpPath, aimPath, folder, filename, path, width, height,
                     objs)
    # print(objs)
    logger.info('Done! See {}'.format(tmpPath))

