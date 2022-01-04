'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-08-24 08:54:29
LastEditors: xiaoshuyui
LastEditTime: 2021-02-19 16:37:04
'''
import glob
import os
try:
    import defusedxml.ElementTree as ET
except:
    import xml.etree.ElementTree as ET

from convertmask.utils.methods.logger import logger
from tqdm import tqdm


def x2yConvert(xmlpath, labelPath=''):
    """ this function is used to convert xmls to yolo txts
    
    params:
    xmlpath : xmls saved folder path
    labelPath : can be blank, classes information,like
             '''
             
             classname1

             classname2

             classname3
             
             ...

             '''

    """
    labels = readLabels(labelPath)
    parent_path = os.path.dirname(xmlpath)
    if not os.path.exists(xmlpath):
        raise FileNotFoundError('file not found')
    else:
        if os.path.isfile(xmlpath):
            # pass
            logger.info('single file found')

            labels = readXmlSaveTxt(xmlpath, parent_path, labels)
            if len(labels) > 0:
                logger.warning('generate label file automaticly')
                with open(parent_path + os.sep + 'labels_.txt', 'w') as f:
                    for i in labels:
                        f.write(i + '\n')

            print('Done!')
            print("see here {}".format(parent_path))

        else:
            xmls = glob.glob(xmlpath + os.sep + "*.xml")
            if not os.path.exists(parent_path + os.sep + 'txts_'):
                os.mkdir(parent_path + os.sep + 'txts_')
            logger.info('exists {} xml files'.format(len(xmls)))

            for xml in tqdm(xmls):
                labels = readXmlSaveTxt(xml, parent_path + os.sep + 'txts_',
                                        labels)

            if len(labels) > 0:
                logger.warning('generate label file automaticly')
                with open(
                        parent_path + os.sep + 'txts_' + os.sep +
                        'labels_.txt', 'w') as f:
                    for i in labels:
                        f.write(i + '\n')

            logger.info('Done!')
            logger.info("see here {}".format(parent_path + os.sep + 'txts_'))


def readLabels(labelPath):
    if os.path.exists(labelPath):
        try:
            labels = open(labelPath).read().strip().split('\n')
        except:
            labels = []
    else:
        labels = []

    return labels


def convert(size, box):  # 归一化操作
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)


def readXmlSaveTxt(xmlPath, parent_path, labels=[]):
    classSet = set(labels)
    fileName = xmlPath.split(os.sep)[-1].replace('.xml', '')
    out_file = open(parent_path + os.sep + fileName + '.txt', 'w')

    in_file = open(xmlPath)
    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)

    flag = False

    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        clas = obj.find('name').text

        if not clas in classSet:
            classSet.add(clas)
            labels.append(clas)
            flag = True

        cls_id = labels.index(clas)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text),
             float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
        bb = convert((w, h), b)
        out_file.write(
            str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')

    out_file.close()
    in_file.close()

    if flag:
        return labels
    else:
        return []
