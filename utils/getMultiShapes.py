'''
@lanhuage: python
@Descripttion: 
@version: beta
@Author: xiaoshuyui
@Date: 2020-06-12 09:44:19
@LastEditors: xiaoshuyui
@LastEditTime: 2020-06-15 15:16:35
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

def readYmal(filepath,labeledImg=None):
    if os.path.exists(filepath):
        f = open(filepath)
        y = yaml.load(f)
        f.close()
        # print(y)
        tmp = y['label_names']
        objs = zip(tmp.keys(),tmp.values())
        return sorted(objs)
    elif labeledImg  is not  None:
        """
        should make sure your label is correct!!!

        untested!!!

        6.15 this section is bad
        """
        labeledImg = np.array(labeledImg,dtype=np.uint8)

        # for one class
        labeledImg[labeledImg>127] = 255
        labeledImg[labeledImg!=255] = 0
        labeledImg = labeledImg/255


        labels = labeledImg.ravel()[np.flatnonzero(labeledImg)]

        classes = []
        for i in range(0,len(labels)):
            classes.append("class{}".format(i))
        
        return zip(classes,labels)
    else:
        raise FileExistsError('file not found')



        




def test():
    """
    do not use cv2.imread to load the label img. there is a bug
    """
    # oriImgPath = 'D:\\testALg\\mask2json\\mask2json\\static\\multi_objs_sameclass.jpg'
    # label_img = io.imread('D:\\testALg\\mask2json\\mask2json\\multi_objs_sameclass_json\\label.png')

    oriImgPath = 'D:\\testALg\\mask2json\\mask2json\\static\\multi_objs.jpg'
    label_img = io.imread('D:\\testALg\\mask2json\\mask2json\\multi_objs_json\\label.png')

    labelShape = label_img.shape
    
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

            region = process(img.astype(np.uint8)) 

            """
            this if...else... is unnecessary if using getShape.getMultiRegion 
            """
            if isinstance(region,np.ndarray):
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

            elif isinstance(region,list):
                for subregion in region:
                    points = []
                    for i in range(0,subregion.shape[0]):
                        # print(region[i][0])
                        points.append(subregion[i][0].tolist())
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

    with open('D:\\testALg\\mask2json\\mask2json\\static\\multi_objs.json','w') as f:
        f.write(j)

    
    rmQ.rm('D:\\testALg\\mask2json\\mask2json\\static\\multi_objs.json')


def getMultiShapes(oriImgPath,labelPath,savePath,labelYamlPath=''):
    """
    oriImgPath : for change img to base64
    labelPath : after fcn/unet or other machine learning objects outlining , the generated label img
                or labelme labeled imgs(after json files converted to mask files)
    savePath : json file save path
    labelYamlPath : after json files converted to mask files. if doesn't have this file,should have a labeled img.
                    but the classes should change bu yourself(labelme 4.2.9 has a bug,when change the label there will be an error.
                    ) 

    """
    label_img = io.imread(labelPath)

    if np.max(label_img)>127:
        print('too many classes! \n maybe binary?')
        label_img[label_img>127] = 255
        label_img[label_img!=255] = 0
        label_img = label_img/255

    labelShape = label_img.shape
    
    labels = readYmal(labelYamlPath,label_img)
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

            region = process(img.astype(np.uint8))
           
            if isinstance(region,np.ndarray):
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

            elif isinstance(region,list):
                for subregion in region:
                    points = []
                    for i in range(0,subregion.shape[0]):
                        # print(region[i][0])
                        points.append(subregion[i][0].tolist())
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