'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-08-21 08:52:18
LastEditors: xiaoshuyui
LastEditTime: 2020-08-21 11:10:36
'''
import sys
sys.path.append("..")
import os

from convertmask.mask2json_utils.imgAug_nolabel import imgFlip,imgNoise,imgRotation,imgTranslation,aug_labelme
BASE_DIR = os.path.abspath(os.path.dirname(os.getcwd())) +os.sep + 'static'
# print(BASE_DIR)
imgPath = BASE_DIR + os.sep + 'multi_objs.jpg'
labelPath = BASE_DIR + os.sep + 'multi_objs.json'

if __name__ == "__main__":
    # imgFlip(imgPath)

    imgNoise(imgPath)

    # imgRotation(imgPath)

    # imgTranslation(imgPath)

    # aug_labelme(imgPath)