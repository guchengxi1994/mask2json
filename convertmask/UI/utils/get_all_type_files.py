'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-11-19 08:48:36
LastEditors: xiaoshuyui
LastEditTime: 2020-11-19 08:51:06
'''
import glob
import os


def getFiles(path:str,types:list):
    resList = []
    for t in types:
        resList.extend(glob.glob(path+os.sep+t))
    
    return resList