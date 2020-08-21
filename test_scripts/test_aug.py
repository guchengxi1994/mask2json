'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-08-21 10:36:01
LastEditors: xiaoshuyui
LastEditTime: 2020-08-21 10:39:17
'''
import sys
sys.path.append("..")


from mask2json_utils.imgAug_script import *

if __name__ == "__main__":
    imgAug_withoutLabels('D:\\testALg\\mask2json\\mask2json\\static\\testAug')