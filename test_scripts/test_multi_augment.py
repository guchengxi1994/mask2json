'''
lanhuage: python
Descripttion: multiple image augmentation script.
version: beta
Author: xiaoshuyui
Date: 2020-10-12 10:28:37
LastEditors: xiaoshuyui
LastEditTime: 2020-10-21 16:18:09
'''
import sys

sys.path.append('..')
import os

# from convertmask.utils.imgAug import imgFlip, imgNoise, imgRotation, imgTranslation, aug_labelme, aug_labelimg
from convertmask.utils.img_augment_script import imgAug_LabelImg, imgAug_withLabels

BASE_DIR = os.path.abspath(os.path.dirname(os.getcwd())) + os.sep + 'static'
# print(BASE_DIR)
imgPath = BASE_DIR + os.sep + 'multi_objs.jpg'
labelPath = BASE_DIR + os.sep + 'multi_objs.json'

imgPath2 = BASE_DIR + os.sep + 'label_255.png'
labelPath2 = BASE_DIR + os.sep + 'label_255.xml'

yamlFilePath = BASE_DIR + os.sep + 'multi_objs.yaml'

txtFilePath = BASE_DIR + os.sep + 'multi_objs.txt'

if __name__ == "__main__":
    imgAug_withLabels(imgPath, labelPath, number=1, yamlFilePath=yamlFilePath)

    # imgAug_LabelImg(imgPath2, labelPath2, number=2, yamlFilePath=txtFilePath)
