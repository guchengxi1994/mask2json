'''
lanhuage: python
Descripttion: test my yaml reader.
version: beta
Author: xiaoshuyui
Date: 2020-10-12 09:21:32
LastEditors: xiaoshuyui
LastEditTime: 2020-10-20 09:46:54
'''
import sys

sys.path.append('..')
import os

import yaml
from convertmask.utils.methods.yamlUtils import *

print(yaml.__version__)
del yaml

fileDir = os.path.abspath(os.path.dirname(os.getcwd())) + os.sep + 'static'

if __name__ == "__main__":
    yamlFilePath = fileDir + os.sep + 'info2.yaml'
    
    tmp = readYamlFile(yamlFilePath)
    # tmp.clear()
    # tmp = 'ssss'
    # print(tmp)
    li,na,sec = getSection(tmp)

    for i in li:
        print(i)
