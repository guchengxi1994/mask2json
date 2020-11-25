'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-11-25 13:43:36
LastEditors: xiaoshuyui
LastEditTime: 2020-11-25 15:35:57
'''
import sys

sys.path.append("..")

import os
from convertmask.utils.negativeSampleGenerate.genrate import NegativeSampleGenerater
from skimage import io

BASE_DIR = os.path.abspath(os.path.dirname(os.getcwd())) + os.sep + 'static'

if __name__ == "__main__":
    n = NegativeSampleGenerater(
        'D:\\facedetect\\dump\\WIDER_train\\imgs\\',
        'D:\\facedetect\\dump\\xmls_\\',
        'notAface',
        saveFilePath='D:\\facedetect\\dump\\genXmls\\',
        multiProcesses=True)

    # n = NegativeSampleGenerater(
    #     'D:\\facedetect\\dump\\WIDER_train\\imgs\\0_Parade_marchingband_1_5.jpg',
    #     'D:\\facedetect\\dump\\xmls_\\0_Parade_marchingband_1_5.xml',
    #     'notAface',
    #     saveFilePath='D:\\facedetect\\dump\\genXmls\\',
    #     multiProcesses=False)
    
    n.go()
