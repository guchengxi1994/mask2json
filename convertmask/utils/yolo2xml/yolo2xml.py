'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-10-12 15:47:58
LastEditors: xiaoshuyui
LastEditTime: 2021-02-19 14:56:42
'''
import glob
import os
# import xml.etree.ElementTree as ET

from convertmask.utils.img2xml.processor_multi_object import img2xml_multiobj
from convertmask.utils.methods.logger import logger
from convertmask.utils.xml2yolo.xml2yolo import readLabels
from skimage import io
from tqdm import tqdm


def y2xConvert(txtPath, imgPath, labelPath):
    """ this function is used to convert yolo txts to xml files(in order to change)
    
    params:
    txtPath : yolo txts saved folder path
    imgPath : images saved folder
    labelPath : classes information,like
             '''
             
             classname1

             classname2

             classname3
             
             ...

             '''

    """
    logger.info('only *.jpg supported right now!')
    labels = readLabels(labelPath)
    if not os.path.exists(txtPath):
        raise FileNotFoundError('file not found')
    else:
        if os.path.isfile(txtPath):
            # pass
            parent_path = os.path.dirname(txtPath)
            filename = os.path.split(imgPath)[1]
            imgname = os.path.splitext(filename)[0]
            logger.info('single file found')
            image = io.imread(imgPath)
            folder = os.path.dirname(imgPath)
            imgShape = image.shape
            objs = []
            with open(txtPath, 'r', encoding='utf-8') as f:
                contents = f.readlines()

            if len(contents) > 0:
                for c in contents:
                    obj = dict()
                    tmp = c.split(' ')
                    clas, x, y, w, h = int(
                        tmp[0]), tmp[1], tmp[2], tmp[3], tmp[4]

                    bbox = convert(imgShape, float(x), float(y), float(w),
                                   float(h))
                    # print(bbox)
                    obj['name'] = labels[clas]
                    obj['difficult'] = 0
                    obj['bndbox'] = {
                        'xmin': bbox[0],
                        'ymin': bbox[2],
                        'xmax': bbox[1],
                        'ymax': bbox[3]
                    }
                    objs.append(obj)

            tmpPath = parent_path + os.sep + '_xmls_' + os.sep + imgname + '.xml'

            if not os.path.exists(parent_path + os.sep + '_xmls_'):
                os.mkdir(parent_path + os.sep + '_xmls_')

            img2xml_multiobj(tmpPath, tmpPath, folder, filename, imgPath,
                             imgShape[1], imgShape[0], objs)

            logger.info('Done! See {} .'.format(tmpPath))

        else:
            logger.info('Multiple files found')
            parent_path = os.path.dirname(txtPath)

            if not os.path.exists(parent_path + os.sep + '_xmls_'):
                os.mkdir(parent_path + os.sep + '_xmls_')

            txts = glob.glob(txtPath + os.sep + "*.txt")
            for i in tqdm(txts):
                filename = os.path.split(i)[1]
                imgname = os.path.splitext(filename)[0]
                i_imgPath = imgPath + os.sep + imgname + '*.jpg'

                if not os.path.exists(i_imgPath):
                    logger.error('image not found!')
                    return

                image = io.imread(i_imgPath)
                folder = imgPath
                imgShape = image.shape
                objs = []
                with open(i, 'r', encoding='utf-8') as f:
                    contents = f.readlines()

                if len(contents) > 0:
                    for c in contents:
                        obj = dict()
                        tmp = c.split(' ')
                        clas, x, y, w, h = int(
                            tmp[0]), tmp[1], tmp[2], tmp[3], tmp[4]

                        bbox = convert(imgShape, float(x), float(y), float(w),
                                       float(h))
                        # print(bbox)
                        obj['name'] = labels[clas]
                        obj['difficult'] = 0
                        obj['bndbox'] = {
                            'xmin': bbox[0],
                            'ymin': bbox[2],
                            'xmax': bbox[1],
                            'ymax': bbox[3]
                        }
                        objs.append(obj)

                tmpPath = parent_path + os.sep + '_xmls_' + os.sep + imgname + '.xml'
                img2xml_multiobj(tmpPath, tmpPath, folder, filename, imgPath,
                                 imgShape[1], imgShape[0], objs)

            logger.info('Done! See {} .'.format(parent_path + os.sep +
                                                '_xmls_'))


def convert(imgShape, x, y, w, h):
    dw = imgShape[0]
    dh = imgShape[1]

    b1 = (2 * x + w) / 2
    b0 = (2 * x - w) / 2
    b3 = (2 * y + h) / 2
    b2 = (2 * y - h) / 2

    b0 = b0 * dw
    b1 = b1 * dw
    b2 = b2 * dh
    b3 = b3 * dh

    return [int(b0), int(b1), int(b2), int(b3)]
