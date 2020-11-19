'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-08-24 08:51:48
LastEditors: xiaoshuyui
LastEditTime: 2020-11-19 09:46:23
'''

__support_img_types__ = ['*.jpg','*.jpeg','*.bmp','*.png']

__support_anno_types__ = ['*.txt','*.json','*.xml']

__support_classfiles_types__ = ['*.txt','*.yaml']

__support_aug_methods__ = ['flip','noise','rotation','translation','zoom']

__support_aug_optional_methods__ = ['crop','distort','inpaint','perspective','resize']

__version__ = '0.5.3'
__appname__ = 'convertmask'
__support_methods__ = [
    'mask2json',
    'mask2xml',
    'json2mask',
    'json2xml',
    'xml2json',
    'yolo2xml',
    'xml2yolo',
    'augmentation',
]

__support_methods_simplified__ = {
    'mask2json': 'm2j',
    'mask2xml': 'm2x',
    'json2mask': 'j2m',
    'json2xml': 'j2x',
    'xml2json': 'x2j',
    'yolo2xml': 'y2x',
    'xml2yolo': 'x2y',
    'augmentation': 'aug',
}

import multiprocessing
__CPUS__ = multiprocessing.cpu_count()
del multiprocessing

import argparse
from convertmask.utils.methods.logger import logger


class BaseParser(object):
    def __init__(self, args: list, appname: str):
        """
        args type:list
        arg type:tuple
        arg example : ('-f','--force','force to show message even do not contain the module')
        """
        self.args = args
        self.appname = __appname__
        self.parser = argparse.ArgumentParser(
            description=
            '{} is a a small tool for image augmentation, including mask files to json/xml files , image augmentation(flip,rotation,noise,...) and so on'
            .format(self.appname))

    def get_parser(self):
        # pass
        return self.parser

    def add_parser(self, arg):
        pass
