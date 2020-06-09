'''
@lanhuage: python
@Descripttion: 
@version: beta
@Author: xiaoshuyui
@Date: 2020-06-09 16:24:12
@LastEditors: xiaoshuyui
@LastEditTime: 2020-06-09 17:34:20
'''
import cv2
from utils import getShape
from utils import img2base64

if __name__ == "__main__":
    img = "D:\\testALg\mask2json\mask2json\static\\1-2cvt.png"

    region = getShape.process(img)
    # print(type(region))
    # print(region.shape)

    for i in range(0,region.shape[0]):
        print(region[i][0])

