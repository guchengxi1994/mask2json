'''
@lanhuage: python
@Descripttion: 
@version: beta
@Author: xiaoshuyui
@Date: 2020-06-09 16:24:12
@LastEditors: xiaoshuyui
@LastEditTime: 2020-06-10 09:22:51
'''
import cv2
from utils import getShape
from utils import img2base64
from utils import rmQ
import json
import os

def test():
    img = "D:\\testALg\mask2json\mask2json\static\\1-2cvt.png"
    oriImg = "D:\\testALg\mask2json\mask2json\static\\1-2cvt.jpg"
    imgShape = cv2.imread(img).shape

    region = getShape.process(img)
    # print(type(region))
    # print(region.shape)
    points = []
    shapes = []
    for i in range(0,region.shape[0]):
        print(region[i][0])
        points.append(region[i][0].tolist())

    obj = dict()
    obj['version'] = '4.2.9'

    obj['flags'] = {}

    shape = dict()
    shape['label'] = 'weld'  #whatever other label
    shape['points'] = points
    shape['group_id']='null'
    shape['shape_type']='polygon'
    shape['flags']={}


    shapes.append(shape)

    obj['shapes'] = shapes
    obj['imagePath'] = oriImg.split(os.sep)[-1]
    obj['imageData'] = str(img2base64.imgEncode(oriImg))
    obj['imageHeight'] = imgShape[0]
    obj['imageWidth'] = imgShape[1]


    j = json.dumps(obj,sort_keys=True, indent=4)

    print(j)

    with open('D:\\testALg\mask2json\mask2json\static\\1-2cvt.json','w') as f:
        f.write(j)

    
    rmQ.rm('D:\\testALg\mask2json\mask2json\static\\1-2cvt.json')

            




if __name__ == "__main__":
    test()



