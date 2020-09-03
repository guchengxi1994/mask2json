'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-09-03 14:17:43
LastEditors: xiaoshuyui
LastEditTime: 2020-09-03 14:45:32
'''
import sys
sys.path.append("..")
import os

from convertmask.utils.longImgSplit import script as sc
save_dir = os.path.abspath(os.path.dirname(os.getcwd())) +os.sep + 'static'+os.sep+"testXmlSplit"+os.sep

if __name__ == "__main__":
    sc.convertImgSplit(save_dir+'1.jpg',save_dir+'1.xml',yamlPath=save_dir+'info2.yaml')
    