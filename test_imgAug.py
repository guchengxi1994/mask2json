'''
@lanhuage: python
@Descripttion: 
@version: beta
@Author: xiaoshuyui
@Date: 2020-07-17 15:49:30
LastEditors: xiaoshuyui
LastEditTime: 2020-08-14 17:10:02
'''

from utils.imgAug import imgFlip
import os

BASE_DIR = os.path.abspath(os.curdir) +os.sep + 'static'

imgPath = BASE_DIR + os.sep + 'multi_objs.jpg'
labelPath = BASE_DIR + os.sep + 'multi_objs.json'

if __name__ == "__main__":
    # print(imgPath)
    imgFlip(imgPath, labelPath)