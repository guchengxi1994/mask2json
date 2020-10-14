'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-08-14 17:01:39
LastEditors: xiaoshuyui
LastEditTime: 2020-10-14 10:52:50
'''


class Ori_Pro(object):
    def __init__(self, oriImg, processedImg):
        self.oriImg = oriImg
        self.processedImg = processedImg


def do_nothing():
    pass


class Img_clasId(object):
    def __init__(self, img, clasId: int):
        self.img = img
        self.clasId = clasId