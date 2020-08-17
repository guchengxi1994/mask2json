'''
@lanhuage: python
@Descripttion: 
@version: beta
@Author: xiaoshuyui
@Date: 2020-07-17 15:49:30
LastEditors: xiaoshuyui
LastEditTime: 2020-08-17 14:10:25
'''

from utils.imgAug import imgFlip,imgNoise,imgRotation
import os

BASE_DIR = os.path.abspath(os.curdir) +os.sep + 'static'

imgPath = BASE_DIR + os.sep + 'multi_objs.jpg'
labelPath = BASE_DIR + os.sep + 'multi_objs.json'

if __name__ == "__main__":

    imgFlip(imgPath, labelPath)

    imgNoise(imgPath,labelPath)

    imgRotation(imgPath,labelPath)