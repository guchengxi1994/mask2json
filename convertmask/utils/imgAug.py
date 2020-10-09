'''
@lanhuage: python
@Descripttion:  (1)get a json file, an origin image \n
                (2)make a convertion \n
                (3)get corresponding json file and converted image
@version: beta
@Author: xiaoshuyui
@Date: 2020-07-17 15:09:27
LastEditors: xiaoshuyui
LastEditTime: 2020-10-09 15:40:35
'''

import sys
sys.path.append('..')
# import warnings
from skimage import io
import skimage.util.noise as snoise
# from skimage import morphology
import cv2
import os
from .json2mask.convert import processor
from .getMultiShapes import getMultiShapes
# from utils.img2base64 import imgEncode
from .methods.img2base64 import imgEncode
from .methods import rmQ
import traceback
# from .entity import *
from .methods.entity import *
import numpy as np
import shutil
import json
# from .logger import logger
from .methods.logger import logger
import random
from convertmask.utils.xml2json.xml2json import x2jConvert_pascal
from convertmask.utils.json2xml.json2xml import j2xConvert



def imgFlip(oriImg:str,oriLabel:str,flip_list=[1,0,-1],flag=True):
    """
    flipList: flip type. see cv2.flip :
    1: 水平翻转 \n
    0: 垂直翻转 \n
    -1: 同时翻转 \n
    >>> import cv2
    >>> help(cv2.flip)
    """
    if isinstance(oriImg,str) :
        if os.path.exists(oriImg):
            img = io.imread(oriImg)
        else:
            raise FileNotFoundError('Original image not found')
    else:
        img = oriImg

    try:
        if len(flip_list)>1 and (1 in flip_list or 0 in flip_list or -1 in flip_list):
            # mask = processor(oriLabel,flag=True)
            if isinstance(oriLabel,str):
                mask = processor(oriLabel,flag=True)
            elif isinstance(oriLabel,np.ndarray):
                mask = oriLabel
            else:
                raise TypeError("input parameter 'oriLabel' type is not supported")
            # print(type(mask))
            h_ori = cv2.flip(img,1)
            v_ori = cv2.flip(img,0)
            h_v_ori = cv2.flip(img,-1)

            h_mask = cv2.flip(mask,1) if 1 in flip_list else None
            v_mask = cv2.flip(mask,0) if 0 in flip_list else None
            h_v_mask = cv2.flip(mask,-1) if -1 in flip_list else None

            """
            maybe dict zip is better :)
            """

            if flag:
                parent_path = os.path.dirname(oriLabel)
                if os.path.exists(parent_path+os.sep+'jsons_'):
                    pass
                else:
                    os.makedirs(parent_path+os.sep+'jsons_')
                fileName = oriLabel.split(os.sep)[-1].replace('.json','')

                io.imsave(parent_path+os.sep+'jsons_'+os.sep+fileName+'_h.jpg',h_ori) if 1 in flip_list else do_nothing()
                io.imsave(parent_path+os.sep+'jsons_'+os.sep+fileName+'_v.jpg',v_ori) if 0 in flip_list else do_nothing()
                io.imsave(parent_path+os.sep+'jsons_'+os.sep+fileName+'_h_v.jpg',h_v_ori) if -1 in flip_list else do_nothing()


                h_j = getMultiShapes(parent_path+os.sep+'jsons_'+os.sep+fileName+'_h.jpg',h_mask,flag=True,labelYamlPath='') if h_mask is not None else None
                # h_j = getMultiShapes(parent_path+os.sep+'jsons_'+os.sep+fileName+'_h.jpg',h_mask,flag=True,labelYamlPath='D:\\testALg\\mask2json\\mask2json\\multi_objs_json\\info.yaml')
                v_j = getMultiShapes(parent_path+os.sep+'jsons_'+os.sep+fileName+'_v.jpg',v_mask,flag=True,labelYamlPath='') if v_mask is not None else None
                h_v_j = getMultiShapes(parent_path+os.sep+'jsons_'+os.sep+fileName+'_h_v.jpg',h_v_mask,flag=True,labelYamlPath='') if h_v_mask is not None else None

                for saveJsonPath in [parent_path+os.sep+'jsons_'+os.sep+fileName+'_h.json',
                                    parent_path+os.sep+'jsons_'+os.sep+fileName+'_v.json',
                                    parent_path+os.sep+'jsons_'+os.sep+fileName+'_H_V.json']:
                    
                    # if saveJsonPath is not None:
                        # print(saveJsonPath)
                    if saveJsonPath.endswith('_h.json')  :   
                        if h_j is not None:
                            with open(saveJsonPath,'w') as f:
                                f.write(h_j)
                        else:
                            pass
                    elif saveJsonPath.endswith('_v.json')  :  
                        if v_j is not None:
                            with open(saveJsonPath,'w') as f:
                                f.write(v_j)
                        else:
                            pass
                    elif saveJsonPath.endswith('_H_V.json') :
                        if h_v_j is not None:
                            with open(saveJsonPath,'w') as f:
                                f.write(h_v_j) 
                        else:
                            pass
                
                    rmQ.rm(saveJsonPath) if os.path.exists(saveJsonPath) else do_nothing()
                
                return ""
            else:

                d = dict()
                d['h'] = Ori_Pro(h_ori,h_mask)
                d['v'] = Ori_Pro(v_ori,v_mask)
                d['h_v'] = Ori_Pro(h_v_ori,h_v_mask)

                return d
                
        else:
            logger.warning("<===== param:flip_list is not valid =====>")



    except Exception :
        # print(e)
        print(traceback.format_exc())


            

def imgNoise(oriImg:str,oriLabel:str,flag=True):
    """
    see skimage.util.random_noise    
    """ 
    noise_type = ['gaussian','poisson','s&p','speckle']
    
    l = np.random.randint(2,size=len(noise_type)).tolist()
    # print(l)
    p = list(zip(noise_type,l))

    if isinstance(oriImg,str) :
        if os.path.exists(oriImg):
            img = io.imread(oriImg)
        else:
            raise FileNotFoundError('Original image not found')
    else:
        img = oriImg
    
    for i in p:
        if i[1]!=0:
            img = snoise.random_noise(img,mode=i[0])
    
    img = np.array(img*255).astype(np.uint8)
    
    if flag:
        parent_path = os.path.dirname(oriLabel)
        if os.path.exists(parent_path+os.sep+'jsons_'):
            pass
        else:
            os.makedirs(parent_path+os.sep+'jsons_')
        fileName = oriLabel.split(os.sep)[-1].replace('.json','')

        io.imsave(parent_path+os.sep+'jsons_'+os.sep+fileName+'_noise.jpg',img) 
        
        try:
            if isinstance(oriLabel,str):
                shutil.copyfile(oriLabel,parent_path+os.sep+'jsons_'+os.sep+fileName+'_noise.json')

                base64code = imgEncode(parent_path+os.sep+'jsons_'+os.sep+fileName+'_noise.jpg')

                with open(parent_path+os.sep+'jsons_'+os.sep+fileName+'_noise.json','r') as f:
                    load_dict = json.load(f)
                
                load_dict['imageData'] = base64code
                
                with open(parent_path+os.sep+'jsons_'+os.sep+fileName+'_noise.json','w') as f:
                    # json.dump(load_dict,parent_path+os.sep+'jsons_'+os.sep+fileName+'_noise.json')
                    f.write(json.dumps(load_dict))

            elif isinstance(oriLabel,np.ndarray):
                """
                labeled file can be an Image
                """
                noisedMask_j = getMultiShapes(parent_path+os.sep+'jsons_'+os.sep+fileName+'_noise.jpg',oriLabel,flag=True,labelYamlPath='')
                with open(parent_path+os.sep+'jsons_'+os.sep+fileName+'_noise.json','w') as f:
                    f.write(json.dumps(noisedMask_j))
        
        except Exception :
            print(traceback.format_exc())
    
    else:
        d = dict()
        # mask = processor(oriLabel,flag=True)
        if isinstance(oriLabel,str):
            mask = processor(oriLabel,flag=True)
        elif isinstance(oriLabel,np.ndarray):
            mask = oriLabel
        else:
            raise TypeError("input parameter 'oriLabel' type is not supported")
        d['noise'] = Ori_Pro(img,mask)

        return d


def imgRotation(oriImg:str,oriLabel:str,angle=30,scale=1,flag=True):
    """
    旋转
    """
    logger.warning('rotation may cause salt-and-pepper noise. in order to solve this issue, small objects may be missing!')
    if isinstance(oriImg,str) :
        if os.path.exists(oriImg):
            img = io.imread(oriImg)
        else:
            raise FileNotFoundError('Original image not found')
    else:
        img = oriImg

    imgShape = img.shape

    if isinstance(oriLabel,str):
        mask = processor(oriLabel,flag=True)
    elif isinstance(oriLabel,np.ndarray):
        mask = oriLabel
    else:
        raise TypeError("input parameter 'oriLabel' type is not supported")


    center = (0.5*imgShape[1],0.5*imgShape[0])
    mat = cv2.getRotationMatrix2D(center,angle,scale)

    affedImg = cv2.warpAffine(img,mat,(imgShape[1],imgShape[0]))
    affedMask = cv2.warpAffine(mask,mat,(imgShape[1],imgShape[0]))
     

    if flag:
        parent_path = os.path.dirname(oriLabel)

        if os.path.exists(parent_path+os.sep+'jsons_'):
            pass
        else:
            os.makedirs(parent_path+os.sep+'jsons_')
        fileName = oriLabel.split(os.sep)[-1].replace('.json','')

        io.imsave(parent_path+os.sep+'jsons_'+os.sep+fileName+'_rotation.jpg',affedImg) 

        affedMask_j = getMultiShapes(parent_path+os.sep+'jsons_'+os.sep+fileName+'_rotation.jpg',affedMask,flag=True,labelYamlPath='') 
        
        saveJsonPath = parent_path+os.sep+'jsons_'+os.sep+fileName+'_rotation.json'
        
        if affedMask_j is not None:
            with open(saveJsonPath,'w') as f:
                f.write(affedMask_j)
        else:
            pass
    
    else:
        d = dict()
        d['rotation'] = Ori_Pro(affedImg,affedMask)

        return d


    
def imgTranslation(oriImg:str,oriLabel:str,flag=True):
    """
    image translation
    """
    if isinstance(oriImg,str) :
        if os.path.exists(oriImg):
            img = io.imread(oriImg)
        else:
            raise FileNotFoundError('Original image not found')
    else:
        img = oriImg

    imgShape = img.shape

    if isinstance(oriLabel,str):
        mask = processor(oriLabel,flag=True)
    elif isinstance(oriLabel,np.ndarray):
        mask = oriLabel
    else:
        raise TypeError("input parameter 'oriLabel' type is not supported")

    
    trans_h = random.randint(0,int(0.5*imgShape[1]))
    trans_v = random.randint(0,int(0.5*imgShape[0]))

    trans_mat = np.float32([[1,0,trans_h],[0,1,trans_v]])

    transImg = cv2.warpAffine(img,trans_mat,(imgShape[1],imgShape[0]))
    transMask = cv2.warpAffine(mask,trans_mat,(imgShape[1],imgShape[0]))

    if flag:
        parent_path = os.path.dirname(oriLabel)

        if os.path.exists(parent_path+os.sep+'jsons_'):
            pass
        else:
            os.makedirs(parent_path+os.sep+'jsons_')
        fileName = oriLabel.split(os.sep)[-1].replace('.json','')

        io.imsave(parent_path+os.sep+'jsons_'+os.sep+fileName+'_translation.jpg',transImg)
        transMask_j = getMultiShapes(parent_path+os.sep+'jsons_'+os.sep+fileName+'_translation.jpg',transMask,flag=True,labelYamlPath='')

        saveJsonPath = parent_path+os.sep+'jsons_'+os.sep+fileName+'_translation.json'

        if transMask_j is not None:
            with open(saveJsonPath,'w') as f:
                f.write(transMask_j)
        else:
            pass
    
    else:
        d = dict()
        d['trans'] = Ori_Pro(transImg,transMask)

        return d


    





def aug_labelme(filepath,jsonpath,augs=None):
    """
    augs: ['flip','noise','affine','rotate','...']
    """
    default_augs = ['noise','rotation','trans','flip']
    if augs is None:
        augs = ['noise','rotation','trans','flip']

    # elif not isinstance(augs,list):
    else:
        if not isinstance(augs,list):
            try:
                augs = list(str(augs))
            except:
                raise ValueError("parameter:aug's type is wrong. expect a string or list,got {}".format(str(type(augs))))
        # else:
        augs = list(set(augs).intersection(set(default_augs)))

        if len(augs)>0 and augs is not None:
            pass
        else:
            logger.warning('augumentation method is not supported.using default augumentation method.')
            augs = ['noise','rotation','trans','flip']

    # l = np.random.randint(2,size=len(augs)).tolist()

    l = np.random.randint(2,size=len(augs))

    if np.sum(l) == 0:
        l[0] = 1
    
    l = l.tolist()

    # print(l)

    p = list(zip(augs,l))

    img = filepath
    processedImg = jsonpath

    for i in p:
        # if i[0]!='flip':
        if i[1] == 1 :
            if i[0] == 'noise':
                n = imgNoise(img,processedImg,flag=False)
                tmp = n['noise']
                img , processedImg = tmp.oriImg , tmp.processedImg

                del n,tmp

            elif i[0] == 'rotation':
                angle = random.randint(-45,45)
                r = imgRotation(img,processedImg,flag=False,angle=angle)
                tmp = r['rotation']
                img , processedImg = tmp.oriImg , tmp.processedImg

                del r,tmp
            
            elif i[0] == 'trans':
                t = imgTranslation(img,processedImg,flag=False)
                tmp = t['trans']
                img , processedImg = tmp.oriImg , tmp.processedImg

                del t,tmp
            
            elif i[0] == 'flip':
                imgList = []
                processedImgList = []
                
                f = imgFlip(img,processedImg,flag=False)
                
                tmp = f['h_v']
                imgList.append(tmp.oriImg)
                processedImgList.append(tmp.processedImg)

                tmp = f['h']
                imgList.append(tmp.oriImg)
                processedImgList.append(tmp.processedImg)

                tmp = f['v']
                imgList.append(tmp.oriImg)
                processedImgList.append(tmp.processedImg)

                img,processedImg = imgList,processedImgList

                del tmp,f,imgList,processedImgList
    
    parent_path = os.path.dirname(filepath)

    if os.path.exists(parent_path+os.sep+'jsons_'):
        pass
    else:
        os.makedirs(parent_path+os.sep+'jsons_')

    fileName = jsonpath.split(os.sep)[-1].replace(".json",'')

    if isinstance(img,np.ndarray):
        io.imsave(parent_path+os.sep+'jsons_'+os.sep+fileName+'_assumble.jpg',img) 
        assumbleJson = getMultiShapes(parent_path+os.sep+'jsons_'+os.sep+fileName+'_assumble.jpg',processedImg,flag=True,labelYamlPath='')    
        saveJsonPath = parent_path+os.sep+'jsons_'+os.sep+fileName+'_assumble.json'
        with open(saveJsonPath,'w') as f:
            f.write(assumbleJson)
        
        print("Done!")
        print("see here {}".format(parent_path+os.sep+'jsons_'))
    
    elif isinstance(img,list):
        for i in range(0,len(img)):
            io.imsave(parent_path+os.sep+'jsons_'+os.sep+fileName+'_assumble{}.jpg'.format(i),img[i])
            assumbleJson = getMultiShapes(parent_path+os.sep+'jsons_'+os.sep+fileName+'_assumble{}.jpg'.format(i),processedImg[i],flag=True,labelYamlPath='')    
            saveJsonPath = parent_path+os.sep+'jsons_'+os.sep+fileName+'_assumble{}.json'.format(i)
            with open(saveJsonPath,'w') as f:
                f.write(assumbleJson)

        print("Done!")
        print("see here {}".format(parent_path+os.sep+'jsons_'))



def aug_labelimg(filepath,xmlpath,augs=None):
    default_augs = ['noise','rotation','trans','flip']
    if augs is None:
        augs = ['noise','rotation','trans','flip']

    # elif not isinstance(augs,list):
    else:
        if not isinstance(augs,list):
            try:
                augs = list(str(augs))
            except:
                raise ValueError("parameter:aug's type is wrong. expect a string or list,got {}".format(str(type(augs))))
        # else:
        augs = list(set(augs).intersection(set(default_augs)))

        if len(augs)>0 and augs is not None:
            pass
        else:
            logger.warning('augumentation method is not supported.using default augumentation method.')
            augs = ['noise','rotation','trans','flip']

    # l = np.random.randint(2,size=len(augs)).tolist()

    l = np.random.randint(2,size=len(augs))

    if np.sum(l) == 0:
        l[0] = 1
    
    l = l.tolist()

    # print(l)

    p = list(zip(augs,l))

    img = filepath
    # processedImg = xmlpath

    jsonpath = x2jConvert_pascal(xmlpath,filepath)
    processedImg = jsonpath

    for i in p:
        # if i[0]!='flip':
        if i[1] == 1 :
            if i[0] == 'noise':
                n = imgNoise(img,processedImg,flag=False)
                tmp = n['noise']
                img , processedImg = tmp.oriImg , tmp.processedImg

                del n,tmp

            elif i[0] == 'rotation':
                angle = random.randint(-45,45)
                r = imgRotation(img,processedImg,flag=False,angle=angle)
                tmp = r['rotation']
                img , processedImg = tmp.oriImg , tmp.processedImg

                del r,tmp
            
            elif i[0] == 'trans':
                t = imgTranslation(img,processedImg,flag=False)
                tmp = t['trans']
                img , processedImg = tmp.oriImg , tmp.processedImg

                del t,tmp
            
            elif i[0] == 'flip':
                imgList = []
                processedImgList = []
                
                f = imgFlip(img,processedImg,flag=False)
                
                tmp = f['h_v']
                imgList.append(tmp.oriImg)
                processedImgList.append(tmp.processedImg)

                tmp = f['h']
                imgList.append(tmp.oriImg)
                processedImgList.append(tmp.processedImg)

                tmp = f['v']
                imgList.append(tmp.oriImg)
                processedImgList.append(tmp.processedImg)

                img,processedImg = imgList,processedImgList

                del tmp,f,imgList,processedImgList
    
    parent_path = os.path.dirname(filepath)

    if os.path.exists(parent_path+os.sep+'xmls_'):
        pass
    else:
        os.makedirs(parent_path+os.sep+'xmls_')
    
    fileName = jsonpath.split(os.sep)[-1].replace(".json",'')


    if isinstance(img,np.ndarray):
        io.imsave(parent_path+os.sep+'xmls_'+os.sep+fileName+'_assumble.jpg',img) 
        assumbleJson = getMultiShapes(parent_path+os.sep+'xmls_'+os.sep+fileName+'_assumble.jpg',processedImg,flag=True,labelYamlPath='')    
        saveJsonPath = parent_path+os.sep+'xmls_'+os.sep+fileName+'_assumble.json'
        with open(saveJsonPath,'w') as f:
            f.write(assumbleJson)
        
        j2xConvert(saveJsonPath)
        os.remove(saveJsonPath)
        print("Done!")
        print("see here {}".format(parent_path+os.sep+'xmls_'))
    
    elif isinstance(img,list):
        for i in range(0,len(img)):
            io.imsave(parent_path+os.sep+'xmls_'+os.sep+fileName+'_assumble{}.jpg'.format(i),img[i])
            assumbleJson = getMultiShapes(parent_path+os.sep+'xmls_'+os.sep+fileName+'_assumble{}.jpg'.format(i),processedImg[i],flag=True,labelYamlPath='')    
            saveJsonPath = parent_path+os.sep+'xmls_'+os.sep+fileName+'_assumble{}.json'.format(i)
            with open(saveJsonPath,'w') as f:
                f.write(assumbleJson)
            
            j2xConvert(saveJsonPath)
            os.remove(saveJsonPath)

        print("Done!")
        print("see here {}".format(parent_path+os.sep+'xmls_'))
    

    

    

