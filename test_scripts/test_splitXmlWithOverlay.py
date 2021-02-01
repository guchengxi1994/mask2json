'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2021-02-01 12:24:34
LastEditors: xiaoshuyui
LastEditTime: 2021-02-01 14:35:10
'''

import sys

sys.path.append("..")
from convertmask.utils.longImgSplit.script import splitLongImagesWithOverlay

if __name__ == '__main__':
    splitLongImagesWithOverlay('D:\\129\\defects\\images\\hbtjy\\','D:\\129\\tjysign\\','D:\\129\\defects\\save\\')