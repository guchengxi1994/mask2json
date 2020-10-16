'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-08-21 08:52:18
LastEditors: xiaoshuyui
LastEditTime: 2020-10-10 09:44:28
'''
import sys
sys.path.append("..")
import os

from convertmask.utils.imgAug_nolabel import imgFlip, imgNoise, imgRotation, imgTranslation, aug_labelme
BASE_DIR = os.path.abspath(os.path.dirname(os.getcwd())) + os.sep + 'static'

imgPath = BASE_DIR + os.sep + 'multi_objs.jpg'
labelPath = BASE_DIR + os.sep + 'multi_objs.json'

if __name__ == "__main__":
    # imgFlip(imgPath)

    imgNoise(imgPath)

    # imgRotation(imgPath)

    # imgTranslation(imgPath)

    # aug_labelme(imgPath)