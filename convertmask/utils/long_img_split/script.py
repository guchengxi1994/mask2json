'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-09-03 11:41:14
LastEditors: xiaoshuyui
LastEditTime: 2021-02-19 16:47:41
'''
import copy
import os
import shutil
try:
    import defusedxml.ElementTree as ET
except:
    import xml.etree.ElementTree as ET
from glob import glob
from multiprocessing import Pool

import tqdm
from convertmask import __CPUS__, baseDecorate, do_nothing
from convertmask.utils.auglib.optional.paddingAndCut import padForSplitScript
from convertmask.utils.methods.get_multi_shapes import getMultiObjs_voc_withYaml
from convertmask.utils.methods.logger import logger
from convertmask.utils.xml2mask import x2m
from skimage import io

from .split_img import reshape_dengbili, splitImg_cover, splitImg_dengbili

# import json
# from convertmask.utils.json2xml.json2xml import j2xConvert
# import glob

# save_cache_dir = os.path.abspath(os.path.dirname(os.getcwd())) +os.sep + 'cache'
save_ori_dir = os.path.abspath(os.path.dirname(os.getcwd())) + os.sep + 'ori'
save_xml_dir = os.path.abspath(os.path.dirname(os.getcwd())) + os.sep + 'xml'

# if not os.path.exists(save_cache_dir):
#     os.mkdir(save_cache_dir)

if not os.path.exists(save_ori_dir):
    os.mkdir(save_ori_dir)

if not os.path.exists(save_xml_dir):
    os.mkdir(save_xml_dir)


@baseDecorate()
def convertImgSplit(oriImg: str,
                    mask_or_xml: str,
                    labelpath='',
                    yamlPath: str = '',
                    bias=2000):
    imgName = oriImg.split(os.sep)[-1][:-4]
    logger.warning("there is a issue related to  Image Binarization")
    
    if mask_or_xml.endswith('xml'):
        _, maskPath = x2m.x2mConvert(mask_or_xml, labelpath, yamlPath)
        maskImg = io.imread(maskPath)

    else:
        maskImg = mask_or_xml

    splitMaskImgList = splitImg_dengbili(reshape_dengbili(maskImg),
                                         bias=bias,
                                         savefile=False)

    splitMaskOriList = splitImg_dengbili(reshape_dengbili(io.imread(oriImg)),
                                         bias=bias,
                                         savefile=False)

    for i in range(0, len(splitMaskImgList)):
        tmpPath = save_ori_dir + os.sep + imgName + '_{}.jpg'.format(i)
        io.imsave(tmpPath, splitMaskOriList[i])

        getMultiObjs_voc_withYaml(tmpPath,
                                  splitMaskImgList[i],
                                  yamlPath=yamlPath)
    #     tmp = getMultiShapes(tmpPath,splitMaskImgList[i],flag=True,labelYamlPath=yamlPath)
    #     # print(tmp)
    #     tmpJsonPath = save_xml_dir+os.sep+imgName+'_{}.json'.format(i)

    #     with open(tmpJsonPath,'w',encoding='utf-8') as f:
    #         json.dump(json.loads(tmp),f,indent=4)

    #     j2xConvert(tmpJsonPath)

    # try:
    #     jsons = glob.glob(save_xml_dir+os.sep+'*.json')

    # for i in jsons:
    #     os.remove(i)
    # except:
    #     logger.error('delete cache json file failed')


def splitSingleImages(i: str, savepath, xmlpath):
    oriImg = io.imread(i)
    imgList, overLayImgList = splitImg_cover(oriImg)

    _, ext = os.path.splitext(i)
    xml = i.replace(savepath, xmlpath).replace(ext, '.xml')

    _, imgname = os.path.split(i)
    imgname = imgname.replace(ext, '')

    if os.path.exists(xml):
        tree = ET.parse(xml)
        root = tree.getroot()
    else:
        tree = None
        root = None

    for j in range(0, len(imgList)):
        subImg = imgList[j]
        if j != len(imgList) - 1:
            subOverLayImg = overLayImgList[j]
            tmp = str(subOverLayImg.ID).replace('.', 'dot')
            io.imsave(savepath + os.sep + imgname + tmp + '.jpg',
                      subOverLayImg.img)
        else:
            subOverLayImg = None
        io.imsave(savepath + os.sep + imgname + str(subImg.ID) + '.jpg',
                  subImg.img)
        if root is not None:
            subImgTree = copy.deepcopy(tree)
            subImgRoot = subImgTree.getroot()
            size = subImgRoot.find('size')
            size.find('width').text = str(subImg.width)
            size.find('height').text = str(subImg.height)
            subs = subImgRoot.findall('object')
            for obj in subs:
                xmlbox = obj.find('bndbox')
                b = (float(xmlbox.find('xmin').text),
                     float(xmlbox.find('xmax').text),
                     float(xmlbox.find('ymin').text),
                     float(xmlbox.find('ymax').text))
                oriWidth = float(xmlbox.find('xmax').text) - float(
                    xmlbox.find('xmin').text)
                xmlbox.find('xmin').text = str(
                    int(float(xmlbox.find('xmin').text) -
                        j * subImg.width)) if float(xmlbox.find(
                            'xmin').text) - j * subImg.width > 0 else str(0)
                xmlbox.find('xmax').text = str(
                    int(float(xmlbox.find('xmax').text) - j * subImg.width)
                ) if float(xmlbox.find(
                    'xmax').text) - j * subImg.width < subImg.width else str(
                        subImg.width)
                if b[1] < j * subImg.width or b[0] > ((j + 1) * subImg.width):
                    subImgRoot.remove(obj)

                if xmlbox:
                    if int(xmlbox.find('xmax').text) - int(
                            xmlbox.find('xmin').text) < 0.5 * oriWidth:
                        try:
                            subImgRoot.remove(obj)
                        except:
                            pass

            xmlsavepath = savepath + os.sep + imgname + str(subImg.ID) + '.xml'
            subImgTree.write(xmlsavepath)

            if subOverLayImg:
                subOverImgTree = copy.deepcopy(tree)
                subOverImgRoot = subOverImgTree.getroot()
                size = subOverImgRoot.find('size')
                size.find('width').text = str(subOverLayImg.width)
                size.find('height').text = str(subOverLayImg.height)
                subs = subOverImgRoot.findall('object')
                for obj in subs:
                    xmlbox = obj.find('bndbox')
                    oriWidth = float(xmlbox.find('xmax').text) - float(
                        xmlbox.find('xmin').text)
                    b = (float(xmlbox.find('xmin').text),
                         float(xmlbox.find('xmax').text),
                         float(xmlbox.find('ymin').text),
                         float(xmlbox.find('ymax').text))
                    xmlbox.find('xmin').text = str(
                        int(
                            float(xmlbox.find('xmin').text) -
                            (j + 0.5) * subImg.width)
                    ) if float(xmlbox.find('xmin').text) - (
                        j + 0.5) * subImg.width > 0 else str(0)
                    xmlbox.find('xmax').text = str(
                        int(
                            float(xmlbox.find('xmax').text) -
                            (j + 0.5) * subImg.width)
                    ) if float(xmlbox.find('xmax').text) - (
                        j + 0.5) * subImg.width < subImg.width else str(
                            subImg.width)
                    if b[1] < (j + 0.5) * subImg.width or b[0] > (
                        (j + 1.5) * subImg.width):
                        subOverImgRoot.remove(obj)

                    if xmlbox:
                        if int(xmlbox.find('xmax').text) - int(
                                xmlbox.find('xmin').text) < 0.5 * oriWidth:
                            try:
                                subOverImgRoot.remove(obj)
                            except:
                                pass
                tmp = str(subOverLayImg.ID).replace('.', 'dot')
                xmlsavepath = savepath + os.sep + imgname + tmp + '.xml'
                subOverImgTree.write(xmlsavepath)


@baseDecorate(""" this script is used to split imgs into small images,
        eg. 
        a image with width/height = 2, then will be splited into 3 parts;
        a image with width/height = 3, then will be splited into 5 parts;
        a image with width/height = n, then will be splited into (2*n-1) parts;
    """)
def splitLongImagesWithOverlay(imgpath: str,
                               xmlpath: str,
                               savepath: str,
                               imgExt: list = [
                                   "jpg",
                               ],
                               multiprocesses=True,
                               savePaddedFile=False):
    try:
        shutil.rmtree(savepath)
    except:
        pass
    if not os.path.exists(savepath):
        os.mkdir(savepath)
    padForSplitScript(imgpath, savepath, multiprocesses=multiprocesses)
    logger.info('padding images done!')

    imgpaths = []
    for ext in imgExt:
        imgpaths.extend(glob(savepath + '*.{}'.format(ext)))

    if not multiprocesses:
        for i in tqdm.tqdm(imgpaths):

            splitSingleImages(i, savepath, xmlpath)
            if savePaddedFile:
                _, ext = os.path.splitext(i)
                xml = i.replace(savepath, xmlpath).replace(ext, '.xml')
                shutil.copyfile(xml, xml.replace(
                    xmlpath,
                    savepath)) if os.path.exists(xml) else do_nothing()
            os.remove(i)

    else:
        pool = Pool(__CPUS__ - 1)
        pool_list = []

        for i in tqdm.tqdm(imgpaths):
            if savePaddedFile:
                _, ext = os.path.splitext(i)
                xml = i.replace(savepath, xmlpath).replace(ext, '.xml')
                shutil.copyfile(xml, xml.replace(
                    xmlpath,
                    savepath)) if os.path.exists(xml) else do_nothing()
            resultPool = pool.apply_async(splitSingleImages,
                                          (i, savepath, xmlpath))
            pool_list.append(resultPool)

        for pr in tqdm.tqdm(pool_list):
            pr.get()

        if not savePaddedFile:
            logger.info('Delete cache files.')
            for i in tqdm.tqdm(imgpaths):
                os.remove(i)

    logger.info('Done!')
