'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-09-03 07:58:48
LastEditors: xiaoshuyui
LastEditTime: 2021-02-19 16:39:11
'''
import glob
import os
try:
    import defusedxml.ElementTree as ET
except:
    import xml.etree.ElementTree as ET

import numpy as np
import yaml
from convertmask.utils.methods.logger import logger
from convertmask.utils.xml2yolo.xml2yolo import readLabels
from skimage import io
from tqdm import tqdm


def yaml2dict(filepath):
    if os.path.exists(filepath):
        f = open(filepath)
        y = yaml.load(f, Loader=yaml.FullLoader)
        try:
            f.close()
        except:
            pass
        return y
    else:
        raise FileExistsError('file not found')


def labels2yaml(labels: list, savePath='', savefile=True):
    # pass
    if '_background_' not in labels:
        labels.append('_background_')

    tmp = dict()
    tmp['_background_'] = 0
    classId = 1
    for i in range(0, len(labels)):
        x = labels[i].replace('\n','').strip()
        if x != '_background_':
            tmp[x] = classId
            classId += 1
    data = dict()
    data['label_names'] = tmp
    del tmp

    if savefile:
        try:
            with open(savePath + os.sep + 'info.yaml', 'w',
                      encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True)
            logger.info("successfully convert labels to yaml, see {}".format(
                savePath + os.sep + 'info.yaml'))
        except Exception as e:
            logger.error(e)

    return data


def generateMask(xmlPath, parent_path='', label_masks=None,flag=True):
    # classSet = set(labels)
    if parent_path == '':
        parent_path = os.path.dirname(xmlPath)
    fileName = xmlPath.split(os.sep)[-1].replace('.xml', '')
    # out_file = parent_path+os.sep+fileName+'.jpg'

    in_file = open(xmlPath, encoding='utf-8')
    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)

    mask_img = np.zeros((h, w)).astype(np.uint8)

    generateClass = dict()

    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        clas = obj.find('name').text
        xmlbox = obj.find('bndbox')
        b = (int(xmlbox.find('xmin').text), int(xmlbox.find('xmax').text),
             int(xmlbox.find('ymin').text), int(xmlbox.find('ymax').text))
        # print(b)
        if label_masks is not None:
            try:
                generateClass = label_masks['label_names']
                classId = generateClass.get(clas)

                if classId is not None:
                    mask_img[b[2]:b[3], b[0]:b[1]] = int(classId)

                    # mask_img[b[2]+15:b[3]-15,b[0]+15:b[1]-15] = int(classId)
                else:
                    vals = generateClass.values()
                    classId = max(vals) + 1
                    mask_img[b[2]:b[3], b[0]:b[1]] = int(classId)
                    generateClass[clas] = classId

                    label_masks['label_names'] = generateClass

            except Exception as e:
                logger.error(e)

        else:
            label_masks = dict()
            generateClass[clas] = 1
            generateClass['_background_'] = 0
            label_masks['label_names'] = generateClass
            mask_img[b[2]:b[3], b[0]:b[1]] = 1
            label_masks['label_names'] = generateClass
    
    if flag:
        if not os.path.exists(parent_path + os.sep + 'mask_'):
            os.makedirs(parent_path + os.sep + 'mask_')
        io.imsave(parent_path + os.sep + 'mask_' + os.sep + fileName + '.jpg',
                mask_img)
        # io.imsave(parent_path+os.sep+'mask_'+os.sep+fileName+'.jpg',np.array(mask_img/np.max(mask_img)*255,dtype=np.uint8))
        print('process finished. see {}'.format(parent_path + os.sep + 'mask_' +
                                                os.sep + fileName + '.jpg'))
        return label_masks, parent_path + os.sep + 'mask_' + os.sep + fileName + '.jpg'
    else:
        return label_masks


def x2mConvert(xmlpath, labelPath='', yamlPath=''):
    """this function is used to convert xml to masks

    """
    flagY = True
    flagL = True
    if not os.path.exists(yamlPath):
        logger.info('yaml file not exists!')
        flagY = False
        if not os.path.exists(labelPath):
            logger.info('label file not exists!')
            flagL = False
        else:
            labels = readLabels(labelPath)
            label_masks = labels2yaml(labels, savefile=False)
    else:
        label_masks = yaml2dict(yamlPath)

    parent_path = os.path.dirname(xmlpath)
    if not os.path.exists(xmlpath):
        raise FileNotFoundError('file not found')
    else:
        if os.path.isfile(xmlpath):
            logger.info('single file found')

            if flagY or flagL:
                label_masks, maskPath = generateMask(xmlpath, parent_path,
                                                     label_masks)
            else:
                label_masks, maskPath = generateMask(xmlpath, parent_path)
            print('Done!')

            return label_masks, maskPath

        else:
            xmls = glob.glob(xmlpath + os.sep + "*.xml")
            if not os.path.exists(parent_path + os.sep + 'masks_'):
                os.mkdir(parent_path + os.sep + 'masks_')
            logger.info('exists {} xml files'.format(len(xmls)))

            for xml in tqdm(xmls):
                if flagY or flagL:
                    label_masks = generateMask(xml, parent_path, label_masks)
                else:
                    label_masks = generateMask(xml, parent_path)

            print('Done!')
            print("see here {}".format(parent_path + os.sep + 'masks_'))

            return label_masks, parent_path + os.sep + 'masks_'
