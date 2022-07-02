'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-11-18 09:47:36
LastEditors: xiaoshuyui
LastEditTime: 2020-11-18 10:00:04
'''
import os

from multiprocessing import Pool
from skimage import io

from convertmask import __CPUS__
from convertmask.utils.img2xml.processor_multi_object import img2xml_multiobj
from convertmask.utils.methods.logger import logger
from tqdm import tqdm

BASE_DIR = os.path.abspath(os.path.dirname(os.getcwd()))

def writeXml(imgname, objlist, savepath, folder, name,oriImgPath=''):
    # imgname = lines[start].split('/')[-1]
    xmlname = imgname.replace('.jpg', '.xml').replace('\n', '')
    tmpPath = savepath + xmlname
    path = imgname
    if oriImgPath == '':
        logger.warning('Origin image needed!')
        width = 0
        height = 0
    else:
        oriImg = io.imread(oriImgPath+os.sep+imgname)
        width = oriImg.shape[1]
        height = oriImg.shape[0]
        del oriImg
    objs = []
    # objlist = lines[start + 2:end]
    for ob in objlist:
        # print(ob)
        if len(ob) > 20:
            tmp = ob.split(' ')
            xmin = tmp[0]
            ymin = tmp[1]
            w = tmp[2]
            h = tmp[3]
            xmax = int(xmin) + int(w)
            ymax = int(ymin) + int(h)

            obj = dict()
            obj['name'] = name
            obj['diffcult'] = 0
            bndbox = dict()
            bndbox['xmin'] = xmin
            bndbox['ymin'] = ymin
            bndbox['xmax'] = xmax
            bndbox['ymax'] = ymax
            obj['bndbox'] = bndbox
            objs.append(obj)
    img2xml_multiobj(tmpPath, tmpPath, folder, imgname, path, width, height,
                     objs)
    # gc.collect()


def convertWiderface(filepath: str, savepath='', mProcess=False):
    """Annotation of widerface is like

    0--Parade/0_Parade_marchingband_1_849.jpg

    1
    
    449 330 122 149 0 0 0 0 0 0 

    The format of txt ground truth. \n
    File name \n 
    Number of bounding box \n
    x1, y1, w, h, blur, expression, illumination, invalid, occlusion, pose

    which is not suitable for labelImg. Besides, convertion may take a really long time using single process.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    ids = list(index for (index, d) in enumerate(lines)
               if d.endswith('.jpg\n'))
    # print(len(ids))
    if savepath == '':
        savepath = BASE_DIR + os.sep + 'xmls_'

    if not os.path.isdir(savepath):
        os.mkdir(savepath)

    folder = 'face'
    name = 'face'

    lastImg = lines[ids[-1]]
    imgname = lastImg.split('/')[-1].replace('\n', '')
    xmlname = imgname.replace('.jpg', '.xml')
    tmpPath = savepath + xmlname
    path = imgname
    width = 0
    height = 0
    objs = []
    objlist = lines[ids[-1] + 2:]
    for ob in objlist:
        if len(ob) > 20:
            tmp = ob.split(' ')
            xmin = tmp[0]
            ymin = tmp[1]
            w = tmp[2]
            h = tmp[3]
            xmax = int(xmin) + int(w)
            ymax = int(ymin) + int(h)

            obj = dict()
            obj['name'] = name
            obj['diffcult'] = 0
            bndbox = dict()
            bndbox['xmin'] = xmin
            bndbox['ymin'] = ymin
            bndbox['xmax'] = xmax
            bndbox['ymax'] = ymax
            obj['bndbox'] = bndbox
            objs.append(obj)
    img2xml_multiobj(tmpPath, tmpPath, folder, imgname, path, width, height,
                     objs)

    if not mProcess:
        for i in tqdm(range(len(ids) - 1)):
            start = ids[i]
            end = ids[i + 1]
            imgname = lines[start].split('/')[-1]
            xmlname = imgname.replace('.jpg', '.xml').replace('\n', '')
            tmpPath = savepath + xmlname
            path = imgname
            width = 0  # for test
            height = 0  # for test
            objs = []

            objlist = lines[start + 2:end]
            for ob in objlist:
                # print(ob)
                if len(ob) > 20:
                    tmp = ob.split(' ')
                    xmin = tmp[0]
                    ymin = tmp[1]
                    w = tmp[2]
                    h = tmp[3]
                    xmax = int(xmin) + int(w)
                    ymax = int(ymin) + int(h)

                    obj = dict()
                    obj['name'] = name
                    obj['diffcult'] = 0
                    bndbox = dict()
                    bndbox['xmin'] = xmin
                    bndbox['ymin'] = ymin
                    bndbox['xmax'] = xmax
                    bndbox['ymax'] = ymax
                    obj['bndbox'] = bndbox
                    objs.append(obj)
            img2xml_multiobj(tmpPath, tmpPath, folder, imgname, path, width,
                             height, objs)
        logger.info('Done! See {}.'.format(savepath))
    else:
        pool = Pool(__CPUS__ - 1)
        pool_list = []
        for i in tqdm(range(len(ids) - 1)):
            start = ids[i]
            end = ids[i + 1]
            imgname = lines[start].split('/')[-1]
            objlist = lines[start + 2:end]
            resultsPool = pool.apply_async(
                writeXml, (imgname, objlist, savepath, folder, name))
            pool_list.append(resultsPool)

        for pr in tqdm(pool_list):
            re_list = pr.get()
        
        logger.info('Done! See {}.'.format(savepath))