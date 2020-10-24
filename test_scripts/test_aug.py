'''
lanhuage: python
Descripttion: Deprecated. For more information,see test_imgAug, test_multiAug
version: beta
Author: xiaoshuyui
Date: 2020-08-21 10:36:01
LastEditors: xiaoshuyui
LastEditTime: 2020-10-20 09:35:44
'''
import sys

sys.path.append("..")

from convertmask.utils.imgAug_script import *

if __name__ == "__main__":
    imgAug_withoutLabels('D:\\testALg\\mask2json\\mask2json\\static\\testAug')
