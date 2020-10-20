'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-10-20 10:01:52
LastEditors: xiaoshuyui
LastEditTime: 2020-10-20 10:43:39
'''
from convertmask.utils.methods.logger import logger

import configparser
cfp = configparser.ConfigParser()

import convertmask as U
# print(U.__file__)
import os
BASE_DIR = os.path.abspath(os.path.split(U.__file__)[0])
config_ROOT = BASE_DIR + os.sep  + 'config.ini'
cfp.read(config_ROOT)
del U

def getConfigParam(cfg:configparser.ConfigParser,sectionName:str,propertyName:str):
    return cfg.get(sectionName,propertyName)

def setConfigParam(cfg:configparser.ConfigParser,sectionName:str,propertyName:str,value:str,cfgRoot:str=''):
    cfg.set(sectionName,propertyName,value)

    if os.path.exists(cfgRoot):
        pass
    else:
        global config_ROOT
        cfgRoot = config_ROOT
    
    with open(cfgRoot,'w+') as f:
        f.write(f)


    