'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-11-25 11:06:00
LastEditors: xiaoshuyui
LastEditTime: 2021-02-19 16:43:26
'''
import glob
import os
import random
try:
    import defusedxml.ElementTree as ET
except:
    import xml.etree.ElementTree as ET
from multiprocessing import Pool
from xml.dom.minidom import parse

import numpy as np
from convertmask import __CPUS__, baseDecorate
from convertmask.utils.methods.logger import logger
from skimage import io
from tqdm import tqdm


def appendObj(tree, name: str, bndbox: dict):
    rootNode = tree.documentElement

    main_node = tree.createElement("object")

    name_node = tree.createElement("name")
    name_text_value = tree.createTextNode(name)
    name_node.appendChild(name_text_value)  # 把文本节点挂到name_node节点
    main_node.appendChild(name_node)

    difficult_node = tree.createElement("difficult")
    difficult_text_value = tree.createTextNode(str(0))
    difficult_node.appendChild(difficult_text_value)  # 把文本节点挂到name_node节点
    main_node.appendChild(difficult_node)

    obj_node = tree.createElement("bndbox")
    xmin = tree.createElement('xmin')
    ymin = tree.createElement('ymin')
    xmax = tree.createElement('xmax')
    ymax = tree.createElement('ymax')

    xmin_text = tree.createTextNode(str(bndbox['xmin']))
    ymin_text = tree.createTextNode(str(bndbox['ymin']))
    xmax_text = tree.createTextNode(str(bndbox['xmax']))
    ymax_text = tree.createTextNode(str(bndbox['ymax']))

    xmin.appendChild(xmin_text)
    ymin.appendChild(ymin_text)
    xmax.appendChild(xmax_text)
    ymax.appendChild(ymax_text)

    obj_node.appendChild(xmin)
    obj_node.appendChild(ymin)
    obj_node.appendChild(xmax)
    obj_node.appendChild(ymax)
    main_node.appendChild(obj_node)

    rootNode.appendChild(main_node)

    return tree


def isCross(x, point):
    # pass
    pxmin = point[0][0]
    pymin = point[0][1]
    pxmax = point[1][0]
    pymax = point[1][1]

    xxmin = x[0][0]
    xymin = x[0][1]
    xxmax = x[1][0]
    xymax = x[1][1]

    return (pxmin > xxmin and pymin > xymin and pxmin < xxmax and pymin < xymax
            ) or (pxmax > xxmin and pymax > xymin and pxmax < xxmax
                  and pymax < xymax) or (
                      pxmin > xxmin and pymax > xymin and pxmin < xxmax
                      and pymax < xymax) or (
                          pxmax > xxmin and pymin > xymin and pxmax < xxmax
                          and pymin < xymax) or (
                              pxmin < xxmin and pymin < xymin
                              and pxmin > xxmax and pymin > xymax) or (
                                  pxmax < xxmin and pymax < xymin
                                  and pxmax > xxmax and pymax > xymax) or (
                                      pxmin < xxmin and pymax < xymin
                                      and pxmin > xxmax and pymax > xymax) or (
                                          pxmax < xxmin and pymin < xymin
                                          and pxmax > xxmax and pymin > xymax)


def isIouSatisfied(iou: float, ff: list, boxHeights: list, boxWidths: list,
                   area: int):
    flag = True
    for i in range(0, len(ff)):
        if area / (boxHeights[ff[i]] * boxWidths[ff[i]]) > iou:
            flag = False

    return flag


def go_single(labelpath, imgpath, negativeNumbers, iou, negativeClassName,
              savePath):
    tree = ET.parse(open(labelpath))
    resTree = parse(labelpath)
    root = tree.getroot()
    imgSize = root.find('size')
    imgwidth = imgSize.find('width').text
    imgheight = imgSize.find('height').text

    if int(imgwidth) == 0:
        img = io.imread(imgpath)
        imgwidth = img.shape[1]
        imgheight = img.shape[0]
        del img

    boxHeights = []
    boxWidths = []

    points = []

    # convertmask.utils.xml2mask is not sultable for here
    mask_img = np.zeros((imgheight, imgwidth)).astype(np.uint8)
    for obj in root.iter('object'):
        # clas = obj.find('name').text
        xmlbox = obj.find('bndbox')
        b = (int(xmlbox.find('xmin').text), int(xmlbox.find('xmax').text),
             int(xmlbox.find('ymin').text), int(xmlbox.find('ymax').text))
        boxHeights.append(b[3] - b[2])
        boxWidths.append(b[1] - b[0])
        mask_img[b[2]:b[3], b[0]:b[1]] = 1
        points.append([(b[0], b[2]), (b[1], b[3])])

    # generate negative samples
    maxBoxHeight = max(boxHeights)
    minBoxHeight = min(boxHeights)

    maxBoxWidth = max(boxWidths)
    minBoxWidth = max(boxWidths)

    # rate = max(maxBoxWidth/minBoxWidth,maxBoxHeight/minBoxHeight)

    for _ in range(0, negativeNumbers):
        for _ in range(0, 5):
            startPoint = (random.randint(0, imgheight),
                          random.randint(0, imgwidth))
            randomWidth = random.randint(minBoxWidth, maxBoxWidth)
            randomHeight = random.randint(minBoxHeight, maxBoxHeight)
            tmpMask = np.zeros((imgheight, imgwidth)).astype(np.uint8)
            tmpMask[startPoint[0]:startPoint[0] + randomHeight,
                    startPoint[1]:startPoint[1] + randomWidth] = 1

            resTmpMask = tmpMask * mask_img

            point = [(startPoint[1], startPoint[0]),
                     (startPoint[1] + randomWidth,
                      startPoint[0] + randomHeight)]

            # f = len(
            #     list(
            #         filter(
            #             lambda x:
            #             (point[0][0] >= x[0][0] + 0.5*(x[1][0]-x[0][0]) and point[0][1] >= x[0][1] + 0.5*(x[1][1]-x[0][1]) and
            #              point[1][0] >= x[1][0] and point[1][1] >= x[1][1]) or
            #             (point[0][0] <= x[0][0] and point[0][1] <= x[0][1] and
            #              point[1][0] <= x[1][0] - 0.5*(x[1][0]-x[0][0]) and point[1][1] <= x[1][1] - 0.5*(x[1][1]-x[0][1])) or
            #             (point[0][0] >= x[0][0] and point[0][1] >= x[0][1] and
            #              point[1][0] <= x[1][0] and point[1][1] <= x[1][1]) or
            #             (point[0][0] <= x[0][0] and point[0][1] <= x[0][1] and
            #              point[1][0] >= x[1][0] and point[1][1] >= x[1][1]),
            #             points))) == 1

            ff = list(index for (index, x) in enumerate(points)
                      if np.sum(resTmpMask) > 0 and isCross(x, point))

            if len(ff)>0:
                print(ff)
            f = isIouSatisfied(iou, ff, boxHeights, boxWidths,
                               np.sum(resTmpMask))

            # f = len(
            #     list(
            #         filter(
            #             lambda x:
            #             (point[0][0] <= x[0][0] and point[0][1] <= x[0][1] and
            #              point[1][0] >= x[1][0] and point[1][1] >= x[1][1]),
            #             points))) < 1

            if np.sum(resTmpMask) == 0 or f:
                mask_img[startPoint[0]:startPoint[0] + randomHeight,
                         startPoint[1]:startPoint[1] + randomWidth] = 1

                xmin = startPoint[1]
                ymin = startPoint[0]

                xmax = startPoint[1] + randomWidth if startPoint[
                    1] + randomWidth < imgwidth else imgwidth
                ymax = startPoint[0] + randomHeight if startPoint[
                    0] + randomHeight < imgheight else imgheight

                name = negativeClassName
                o = dict()
                o['xmin'] = xmin
                o['ymin'] = ymin
                o['xmax'] = xmax
                o['ymax'] = ymax

                if xmax - xmin > 0.5 * minBoxWidth and ymax - ymin > 0.5 * minBoxHeight:
                    resTree = appendObj(resTree, name, o)
                    # points.append(point)
                break

    with open(savePath, 'w') as f:
        resTree.writexml(f, addindent='  ', encoding='utf-8')


class NegativeSampleGenerater(object):
    def __init__(self,
                 img_or_path: str,
                 label_or_path: str,
                 negativeClassName: str = 'notAobject',
                 negativeNumbers: int = 10,
                 classFilePath: str = '',
                 saveFilePath: str = '',
                 iou: float = 0.1,
                 multiProcesses: bool = True) -> None:
        self.img_or_path = img_or_path
        self.label_or_path = label_or_path
        self.classFilePath = classFilePath
        self.negativeClassName = negativeClassName
        self.iou = iou
        self.negativeNumbers = negativeNumbers
        self.saveFilePath = saveFilePath
        self.multiProcesses = multiProcesses

    @baseDecorate()
    def go(self, **kwargs):
        if not os.path.exists(self.img_or_path) or not os.path.exists(
                self.label_or_path):
            logger.error('File or path not exists!')
            return

        # single file
        if os.path.isfile(self.label_or_path):
            # xml format
            _, filename = os.path.split(self.label_or_path)
            if self.saveFilePath == '':
                savePath = self.label_or_path
            else:
                savePath = self.saveFilePath + os.sep + filename

            go_single(self.label_or_path, self.img_or_path,
                      self.negativeNumbers, self.iou, self.negativeClassName,
                      savePath)

        else:
            xmls = glob.glob(self.label_or_path + os.sep + '*.xml')
            if not self.multiProcesses:
                for i in tqdm(xmls):
                    _, filename = os.path.split(i)
                    if self.saveFilePath == '':
                        savePath = self.label_or_path
                    else:
                        savePath = self.saveFilePath + os.sep + filename
                    imgpath = self.img_or_path + os.sep + filename.replace(
                        '.xml', '.jpg')
                    go_single(i, imgpath, self.negativeNumbers, self.iou,
                              self.negativeClassName, savePath)

            else:
                pool = Pool(__CPUS__ - 1)
                pool_list = []
                for i in xmls:
                    _, filename = os.path.split(i)
                    if self.saveFilePath == '':
                        savePath = self.label_or_path
                    else:
                        savePath = self.saveFilePath + os.sep + filename
                    imgpath = self.img_or_path + os.sep + filename.replace(
                        '.xml', '.jpg')
                    resultspool = pool.apply_async(
                        go_single, (i, imgpath, self.negativeNumbers, self.iou,
                                    self.negativeClassName, savePath))
                    pool_list.append(resultspool)

                for pr in tqdm(pool_list):
                    re_list = pr.get()
