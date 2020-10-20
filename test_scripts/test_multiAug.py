'''
lanhuage: python
Descripttion: multiple image augmentation script.
version: beta
Author: xiaoshuyui
Date: 2020-10-12 10:28:37
LastEditors: xiaoshuyui
LastEditTime: 2020-10-20 09:45:21
'''
import sys
sys.path.append('..')
import os
# from convertmask.utils.imgAug import imgFlip, imgNoise, imgRotation, imgTranslation, aug_labelme, aug_labelimg
from convertmask.utils.imgAug_script import imgAug_withLabels, imgAug_LabelImg

BASE_DIR = os.path.abspath(os.path.dirname(os.getcwd())) + os.sep + 'static'
# print(BASE_DIR)
imgPath = BASE_DIR + os.sep + 'multi_objs.jpg'
labelPath = BASE_DIR + os.sep + 'multi_objs.json'

imgPath2 = BASE_DIR + os.sep + 'label_255.png'
labelPath2 = BASE_DIR + os.sep + 'label_255.xml'

if __name__ == "__main__":
    imgAug_withLabels(imgPath, labelPath, number=2)

    imgAug_LabelImg(imgPath2, labelPath2, number=50)
