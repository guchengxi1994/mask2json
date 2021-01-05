'''
lanhuage: python
Descripttion: this script is used to solve 'pip install PyYAML' issue. JUST for label yaml file reading. Following https://www.cnblogs.com/aric2016/p/11716961.html
version: beta
Author: xiaoshuyui
Date: 2020-10-12 08:42:02
LastEditors: xiaoshuyui
LastEditTime: 2021-01-05 13:37:15
'''

from convertmask import baseDecorate
import os

import io
from convertmask.utils.methods.logger import logger


class FullLoader():
    pass


class SectionName():
    def __init__(self, sectionName: str, index: int):
        self.sectionName = sectionName
        self.index = index

    def __str__(self):
        return str(self.index) + ":" + str(self.__class__)


class Section():
    def __init__(self, section: list, index: int):
        self.section = section
        self.index = index

    def __str__(self):
        return str(self.index) + ":" + str(self.__class__)


@baseDecorate()
def readYamlFile(filepath: str, encoding='utf-8'):
    if not os.path.exists(filepath):
        logger.error('file not found')
        return

    with open(filepath, 'r', encoding=encoding) as f:
        # print(type(f))
        lis = f.readlines()

    # print(lis)
    return lis


@baseDecorate()
def getSection(li: list):
    # try:
    #     tmp = iter(li)
    # except Exception as e:
    #     logger.error(e)
    #     return
    section = []
    sections = []
    secNum = 0
    secNameNum = 0
    # num = 0
    # for i in li:
    #     # subSection = []
    #     if i.strip(' ').strip('\t') == '\n':
    #         pass
    #     else:
    #         tmp = i.replace('\n','')
    #         if ' ' in i:
    #             subSection.append(tmp)
    #         else:
    # while True:
    #     try:
    # 获得下一个值:
    for i in range(0, len(li)):

        x = li[i]
        # print(x)
        if x.strip(' ').strip('\t') == '\n' or i == len(li) - 1:
            if len(section) > 0:
                sections.append(Section(section, secNum))
                section.clear()
                secNum += 1
        else:
            res = x.replace('\n', '')
            if ' ' in x:
                if not x.strip(' ').startswith('#'):
                    section.append(res)
            else:
                if res.endswith(':'):
                    sectionName = res.replace(':', "")
                    sections.append(SectionName(sectionName, secNameNum))
                    secNameNum += 1

        # except StopIteration:
        #     # 遇到StopIteration就退出循环
        #     break

    return sections, secNameNum, secNum


@baseDecorate()
def load(stream, Loader=None):
    if isinstance(stream, str):
        lis = readYamlFile(stream)
    elif isinstance(stream, io.TextIOWrapper):
        lis = stream.readlines()
    else:
        logger.error('input parameter error.')
        return
    res = dict()
    sections, secNameNum, secNum = getSection(lis)
