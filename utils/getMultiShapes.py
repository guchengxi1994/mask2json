'''
@lanhuage: python
@Descripttion: 
@version: beta
@Author: xiaoshuyui
@Date: 2020-06-12 09:44:19
@LastEditors: xiaoshuyui
@LastEditTime: 2020-06-12 10:50:56
'''
import cv2
import numpy as np
import skimage.io as io
import yaml
import copy
from .getShape import *
from .img2base64 import imgEncode
import os,json
from . import rmQ

def readYmal(filepath):
    f = open(filepath)
    y = yaml.load(f)
    f.close()
    # print(y)
    tmp = y['label_names']
    objs = zip(tmp.keys(),tmp.values())
    return sorted(objs)



def test():
    """
    do not use cv2.imread to load the label img. there is a bug
    """
    oriImgPath = 'D:\\testALg\\mask2json\\mask2json\\static\\multi_objs.jpg'
    label_img = io.imread('D:\\testALg\\mask2json\\mask2json\\multi_objs_json\\label.png')

    labelShape = label_img.shape
    # print(np.max(label_img))
    # label_img[label_img==1] = 255
    # cv2.namedWindow('test', cv2.WINDOW_AUTOSIZE)
    # cv2.imshow('test',label_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    labels = readYmal('D:\\testALg\\mask2json\\mask2json\\multi_objs_json\\info.yaml')
    shapes = []
    obj = dict()
    obj['version'] = '4.2.9'
    obj['flags'] = {}
    for la in labels:
        if la[1]>0:
            # img = label_img[label_img == i[1]]
            img = copy.deepcopy(label_img)
            
            img[img == la[1]] = 255
            img[img!=255] = 0
            # cv2.imwrite('D:\\testALg\\mask2json\\mask2json\\multi_objs_json\\test.jpg',img)
            region = process(img.astype(np.uint8))
            # print(region)
            points = []
            for i in range(0,region.shape[0]):
                # print(region[i][0])
                points.append(region[i][0].tolist())
            shape = dict()
            shape['label'] = la[0]
            shape['points'] = points
            shape['group_id'] = 'null'
            shape['shape_type']='polygon'
            shape['flags']={}

            shapes.append(shape)
    
    obj['shapes'] = shapes
    obj['imagePath'] = oriImgPath.split(os.sep)[-1]
    obj['imageData'] = str(imgEncode(oriImgPath))

    obj['imageHeight'] = labelShape[0]
    obj['imageWidth'] = labelShape[1]

    j = json.dumps(obj,sort_keys=True, indent=4)

    with open('D:\\testALg\mask2json\mask2json\\test.json','w') as f:
        f.write(j)

    
    rmQ.rm('D:\\testALg\mask2json\mask2json\\test.json')


def getMultiShapes(oriImgPath,labelPath,labelYamlPath,savePath):
    label_img = io.imread(labelPath)

    labelShape = label_img.shape
    # print(np.max(label_img))
    # label_img[label_img==1] = 255
    # cv2.namedWindow('test', cv2.WINDOW_AUTOSIZE)
    # cv2.imshow('test',label_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    labels = readYmal(labelYamlPath)
    shapes = []
    obj = dict()
    obj['version'] = '4.2.9'
    obj['flags'] = {}
    for la in labels:
        if la[1]>0:
            # img = label_img[label_img == i[1]]
            img = copy.deepcopy(label_img)
            
            img[img == la[1]] = 255
            img[img!=255] = 0
            # cv2.imwrite('D:\\testALg\\mask2json\\mask2json\\multi_objs_json\\test.jpg',img)
            region = process(img.astype(np.uint8))
            # print(region)
            points = []
            for i in range(0,region.shape[0]):
                # print(region[i][0])
                points.append(region[i][0].tolist())
            shape = dict()
            shape['label'] = la[0]
            shape['points'] = points
            shape['group_id'] = 'null'
            shape['shape_type']='polygon'
            shape['flags']={}

            shapes.append(shape)
    
    obj['shapes'] = shapes
    obj['imagePath'] = oriImgPath.split(os.sep)[-1]
    obj['imageData'] = str(imgEncode(oriImgPath))

    obj['imageHeight'] = labelShape[0]
    obj['imageWidth'] = labelShape[1]

    j = json.dumps(obj,sort_keys=True, indent=4)
    saveJsonPath = savePath+os.sep + obj['imagePath'][:-4] + '.json'
    with open(saveJsonPath,'w') as f:
        f.write(j)

    
    rmQ.rm(saveJsonPath)

    



            
            


if __name__ == "__main__":
    test()