'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-11-18 10:09:21
LastEditors: xiaoshuyui
LastEditTime: 2021-01-04 13:49:00
'''

from convertmask import deprecated

@deprecated()
def cutout():
    print('please use convertmask.utils.auglib.optional.crop instead')