'''
@lanhuage: python
@Descripttion: Deprecated. Just for test. For more information,see convertmask.utils.mask2json_script.
@version: beta
@Author: xiaoshuyui
@Date: 2020-06-09 16:24:12
LastEditors: xiaoshuyui
LastEditTime: 2020-10-20 09:34:55
'''
import sys

import cv2

sys.path.append('..')
import glob
import json
import os

from convertmask.utils import getMultiShapes
from convertmask.utils.methods import getShape, img2base64, rmQ


def test():
    img = "D:\\testALg\mask2json\mask2json\static\\1-2cvt.png"
    oriImg = "D:\\testALg\mask2json\mask2json\static\\1-2cvt.jpg"
    imgShape = cv2.imread(img).shape

    region = getShape.process(img)
    # print(type(region))
    # print(region.shape)
    points = []
    shapes = []
    for i in range(0, region.shape[0]):
        print(region[i][0])
        points.append(region[i][0].tolist())

    obj = dict()
    obj['version'] = '4.2.9'

    obj['flags'] = {}

    shape = dict()
    shape['label'] = 'weld'  #whatever other label
    shape['points'] = points
    shape['group_id'] = 'null'
    shape['shape_type'] = 'polygon'
    shape['flags'] = {}

    shapes.append(shape)

    obj['shapes'] = shapes
    obj['imagePath'] = oriImg.split(os.sep)[-1]
    obj['imageData'] = str(img2base64.imgEncode(oriImg))
    obj['imageHeight'] = imgShape[0]
    obj['imageWidth'] = imgShape[1]

    j = json.dumps(obj, sort_keys=True, indent=4)

    print(j)

    with open('D:\\testALg\mask2json\mask2json\static\\1-2cvt.json', 'w') as f:
        f.write(j)

    rmQ.rm('D:\\testALg\mask2json\mask2json\static\\1-2cvt.json')


def getJsons(imgPath, maskPath, savePath, yamlPath=''):
    """
    imgPath: origin image path \n
    maskPath : mask image path \n
    savePath : json file save path \n
    
    >>> getJsons(path-to-your-imgs,path-to-your-maskimgs,path-to-your-jsonfiles) 

    """
    oriImgs = glob.glob(imgPath + os.sep + '*.jpg')
    maskImgs = glob.glob(maskPath + os.sep + '*.jpg')

    for i in oriImgs:
        i_mask = i.replace(imgPath, maskPath)
        print(i)

        getMultiShapes.getMultiShapes(i, i_mask, savePath, yamlPath)


if __name__ == "__main__":
    # test()
    getJsons('D:\\getWeldPics\\test5_reshape', 'D:\\getWeldPics\\masks',
             'D:\\getWeldPics\\jsons', 'D:\getWeldPics\info.yaml')
