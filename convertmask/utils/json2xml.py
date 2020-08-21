'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-08-19 11:27:38
LastEditors: xiaoshuyui
LastEditTime: 2020-08-19 12:36:22
'''
import json
from .img2xml.processor_multiObj import img2xml_multiobj
import os
import numpy as np

def j2xConvert(jsonFilePath:str):
    with open(jsonFilePath,'r') as f:
        jsonObj = json.load(f)
    
    tmpPath = jsonFilePath.replace('.json','.xml')
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
        bndbox['xmin'] = np.min(tmp[:,0])
        bndbox['xmax'] = np.max(tmp[:,0])
        bndbox['ymin'] = np.min(tmp[:,1])
        bndbox['ymax'] = np.max(tmp[:,1])

        obj['bndbox'] = bndbox

        objs.append(obj)
    
    img2xml_multiobj(tmpPath,aimPath,folder,filename,path,width,height,objs)

        


    

    
    
