'''
@lanhuage: python
@Descripttion: 
@version: beta
@Author: xiaoshuyui
@Date: 2020-06-12 09:44:19
LastEditors: xiaoshuyui
LastEditTime: 2020-10-21 15:24:50
'''
try:
    from labelme import __version__ as labelme_version
except:
    labelme_version = '4.2.9'

import sys

sys.path.append("..")

import copy
import json
import os

import cv2
import numpy as np
import skimage.io as io
import yaml
from convertmask.utils.img2xml.processor_multiObj import img2xml_multiobj
from convertmask.utils.methods import rmQ
from convertmask.utils.methods.getShape import *
from convertmask.utils.methods.img2base64 import imgEncode
# import warnings
from convertmask.utils.methods.logger import logger


def rs(st:str):
    s = st.replace('\n','').strip()
    return s


def readYmal(filepath, labeledImg=None):
    if os.path.exists(filepath):
        if filepath.endswith('.yaml'):
            f = open(filepath)
            y = yaml.load(f, Loader=yaml.FullLoader)
            f.close()
            # print(y)
            tmp = y['label_names']
            objs = zip(tmp.keys(), tmp.values())
            return sorted(objs)
        elif filepath.endswith('.txt'):
            f = open(filepath,'r',encoding='utf-8')
            classList = f.readlines()
            f.close()
            l3 = [rs(i) for i in classList]
            l = list(range(1,len(classList)+1))
            objs = zip(l3,l)
            return sorted(objs)
    elif labeledImg is not None and filepath == "":
        """
        should make sure your label is correct!!!
        """
        labeledImg = np.array(labeledImg, dtype=np.uint8)

        labeledImg[labeledImg > 0] = 255
        labeledImg[labeledImg != 255] = 0

        _, labels, stats, centroids = cv2.connectedComponentsWithStats(
            labeledImg)

        labels = np.max(labels) + 1
        labels = [x for x in range(1, labels)]

        classes = []
        for i in range(0, len(labels)):
            classes.append("class{}".format(i))

        return zip(classes, labels)
    else:
        raise FileExistsError('file not found')


def getMultiObjs_voc(oriImgPath, labelPath, savePath):
    # pass
    labelImg = io.imread(labelPath)
    # print(labelImg.shape)
    (_,fileName) = os.path.split(labelPath)
    # print(fileName)
    # fileName = labelPath.split(os.sep)[-1]
    imgShape = labelImg.shape
    imgHeight = imgShape[0]
    imgWidth = imgShape[1]
    imgPath = oriImgPath
    logger.warning("auto detecting class numbers")
    if len(imgShape) == 3:
        labelImg = labelImg[:, :, 0]
    labelImg[labelImg > 0] = 255

    _, labels, stats, centroids = cv2.connectedComponentsWithStats(labelImg.astype(np.uint8))

    statsShape = stats.shape
    objs = []
    for i in range(1, statsShape[0]):
        st = stats[i, :]

        width = st[2]
        height = st[3]

        xmin = st[0]
        ymin = st[1]

        xmax = xmin + width
        ymax = ymin + height

        ob = {}
        ob['name'] = 'class{}'.format(i)
        ob['difficult'] = 0
        # ob['name'] = 'weld'

        bndbox = {}

        bndbox['xmin'] = xmin
        bndbox['ymin'] = ymin
        bndbox['xmax'] = xmax
        bndbox['ymax'] = ymax

        ob['bndbox'] = bndbox
        objs.append(ob)
    saveXmlPath = savePath + os.sep + fileName[:-4] + '.xml'
    img2xml_multiobj(saveXmlPath, saveXmlPath, "TEST", fileName, imgPath,
                     imgWidth, imgHeight, objs)


def test():
    # BASE_DIR = os.path.abspath(os.curdir)
    BASE_DIR = os.path.abspath(os.path.dirname(os.getcwd()))
    """
    do not use cv2.imread to load the label img. there is a bug
    """
    # oriImgPath = 'D:\\testALg\\mask2json\\mask2json\\static\\multi_objs_sameclass.jpg'
    # label_img = io.imread('D:\\testALg\\mask2json\\mask2json\\multi_objs_sameclass_json\\label.png')

    oriImgPath = BASE_DIR + '/static/multi_objs.jpg'
    label_img = io.imread(BASE_DIR + '/multi_objs_json/label.png')

    labelShape = label_img.shape

    labels = readYmal(BASE_DIR + '/multi_objs_json/info.yaml')
    shapes = []
    obj = dict()
    obj['version'] = labelme_version
    obj['flags'] = {}
    for la in labels:
        if la[1] > 0:
            # img = label_img[label_img == i[1]]
            img = copy.deepcopy(label_img)

            img[img == la[1]] = 255
            img[img != 255] = 0

            region = process(img.astype(np.uint8))
            """
            this if...else... is unnecessary if using getShape.getMultiRegion 
            """
            if isinstance(region, np.ndarray):
                points = []
                for i in range(0, region.shape[0]):
                    # print(region[i][0])
                    points.append(region[i][0].tolist())
                shape = dict()
                shape['label'] = la[0]
                shape['points'] = points
                shape['group_id'] = 'null'
                shape['shape_type'] = 'polygon'
                shape['flags'] = {}
                shapes.append(shape)

            elif isinstance(region, list):
                for subregion in region:
                    points = []
                    for i in range(0, subregion.shape[0]):
                        # print(region[i][0])
                        points.append(subregion[i][0].tolist())
                    shape = dict()
                    shape['label'] = la[0]
                    shape['points'] = points
                    shape['group_id'] = 'null'
                    shape['shape_type'] = 'polygon'
                    shape['flags'] = {}
                    shapes.append(shape)

    obj['shapes'] = shapes
    obj['imagePath'] = oriImgPath.split(os.sep)[-1]
    obj['imageData'] = str(imgEncode(oriImgPath))

    obj['imageHeight'] = labelShape[0]
    obj['imageWidth'] = labelShape[1]

    j = json.dumps(obj, sort_keys=True, indent=4)

    with open(BASE_DIR + '/static/multi_objs.json', 'w') as f:
        f.write(j)

    rmQ.rm(BASE_DIR + '/static/multi_objs.json')


def getMultiShapes(oriImgPath,
                   labelPath,
                   savePath='',
                   labelYamlPath='',
                   flag=False,
                   areaThresh=500):
    """
    oriImgPath : for change img to base64  \n
    labelPath : after fcn/unet or other machine learning objects outlining , the generated label img
                or labelme labeled imgs(after json files converted to mask files)  \n
    savePath : json file save path  \n
    labelYamlPath : after json files converted to mask files. if doesn't have this file,should have a labeled img.
                    but the classes should change by yourself(labelme 4.2.9 has a bug,when change the label there will be an error.
                    )   \n

    """
    # print('-==================')
    # print(oriImgPath)
    # print(labelPath)
    # print(savePath)
    # print(labelYamlPath)
    # print('-==================')
    if isinstance(labelPath, str):
        if os.path.exists(labelPath):
            label_img = io.imread(labelPath)
        else:
            raise FileNotFoundError('mask/labeled image not found')
    else:
        # img = oriImg
        label_img = labelPath
    
    # print(np.max(label_img))

    if np.max(label_img) > 127:
        # print('too many classes! \n maybe binary?')
        label_img[label_img > 127] = 255
        label_img[label_img != 255] = 0
        label_img = label_img / 255

    labelShape = label_img.shape

    labels = readYmal(labelYamlPath, label_img)
    # print(list(labels))
    shapes = []
    obj = dict()
    obj['version'] = labelme_version
    obj['flags'] = {}
    for la in list(labels):

        if la[1] > 0:
            # print(la[0])
            img = copy.deepcopy(label_img)   # img = label_img.copy()
            img = img.astype(np.uint8)

            img[img == la[1]] = 255

            img[img != 255] = 0

            region = process(img.astype(np.uint8))

            if isinstance(region, np.ndarray):
                points = []
                for i in range(0, region.shape[0]):
                    # print(region[i][0])
                    points.append(region[i][0].tolist())
                shape = dict()
                shape['label'] = la[0]
                shape['points'] = points
                shape['group_id'] = 'null'
                shape['shape_type'] = 'polygon'
                shape['flags'] = {}
                shapes.append(shape)

            elif isinstance(region, list):
                # print(len(region))
                for subregion in region:
                    points = []
                    for i in range(0, subregion.shape[0]):
                        points.append(subregion[i][0].tolist())
                    shape = dict()
                    shape['label'] = la[0]
                    shape['points'] = points
                    shape['group_id'] = 'null'
                    shape['shape_type'] = 'polygon'
                    shape['flags'] = {}
                    shapes.append(shape)

    # print(len(shapes))
    obj['shapes'] = shapes
    # print(shapes)
    (_,imgname) = os.path.split(oriImgPath)
    obj['imagePath'] = imgname
    # print(obj['imagePath'])
    obj['imageData'] = str(imgEncode(oriImgPath))

    obj['imageHeight'] = labelShape[0]
    obj['imageWidth'] = labelShape[1]

    j = json.dumps(obj, sort_keys=True, indent=4)

    

    # print(j)

    if not flag:
        saveJsonPath = savePath + os.sep + obj['imagePath'][:-4] + '.json'
        # print(saveJsonPath)
        with open(saveJsonPath, 'w') as f:
            f.write(j)

        rmQ.rm(saveJsonPath)

    else:
        return j


def getMultiObjs_voc_withYaml(oriImgPath, labelPath, yamlPath=''):
    if os.path.exists(yamlPath):
        f = open(yamlPath, encoding='utf-8')
        y = yaml.load(f, Loader=yaml.FullLoader)
        f.close()

        label_masks = y['label_names']
    else:
        raise FileNotFoundError('yaml file not found!')
    # print(label_masks)
    savePath = os.path.abspath(os.path.dirname(oriImgPath)) + os.sep + 'xml'

    if not os.path.exists(savePath):
        os.mkdir(savePath)

    fileName = oriImgPath.split(os.sep)[-1]
    saveXmlPath = savePath + os.sep + fileName[:-4] + '.xml'

    labelImg = io.imread(labelPath) if isinstance(labelPath,
                                                  str) else labelPath
    fileName = oriImgPath.split(os.sep)[-1]
    imgShape = labelImg.shape
    imgHeight = imgShape[0]
    imgWidth = imgShape[1]
    imgPath = oriImgPath
    objs = []
    for k, v in label_masks.items():
        # print(k)
        # print(v)
        ma = copy.deepcopy(labelImg)
        ma[ma != int(v)] = 0

        if np.sum(ma) > 0:
            # print(v)
            ma1 = copy.deepcopy(labelImg)

            ma1[ma1 != int(v)] = 0
            ma1[ma1 != 0] = 255

            _, labels, stats, centroids = cv2.connectedComponentsWithStats(ma1)

            del ma1

            statsShape = stats.shape

            for i in range(1, statsShape[0]):
                st = stats[i, :]
                width = st[2]
                height = st[3]
                xmin = st[0]
                ymin = st[1]

                # print('area = {}'.format(st[4]))
                # print('width = {},height = {}'.format(width,height))

                xmax = xmin + width
                ymax = ymin + height

                ob = {}
                ob['name'] = k
                ob['difficult'] = 0

                bndbox = {}

                bndbox['xmin'] = xmin
                bndbox['ymin'] = ymin
                bndbox['xmax'] = xmax
                bndbox['ymax'] = ymax

                ob['bndbox'] = bndbox
                if width > 10 and height > 10 and st[4] >= 0.75 * (width *
                                                                   height):
                    objs.append(ob)
                    # print(ob)

        del ma

        # print(objs)
    # print("............................")

    img2xml_multiobj(saveXmlPath, saveXmlPath, "TEST", fileName, imgPath,
                     imgWidth, imgHeight, objs)
    objs.clear()


# if __name__ == "__main__":
#     test()
