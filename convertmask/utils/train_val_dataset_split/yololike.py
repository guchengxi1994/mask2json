'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2021-01-13 13:42:14
LastEditors: xiaoshuyui
LastEditTime: 2021-01-13 15:51:15
'''
import glob
import os
from multiprocessing import Pool

from convertmask import __CPUS__
from convertmask.utils.methods.logger import logger
from tqdm import tqdm

from devtool import logit

RES = []


class FileCls:
    def __init__(self, finename: str, clses: dict) -> None:
        self.finename = finename
        self.clses = clses

    def get(self, k):
        return self.clses.get(k, 0)

    def __add__(self, o):
        if not isinstance(o, self.__class__):
            return self
        nc = len(self.clses)
        # c = FileCls()
        for i in range(0, nc):
            sn = self.get(i)
            on = o.get(i)

            self.clses[i] = sn + on

        return self


def getInfo(filename: str, dic: dict):
    # global RES
    with open(filename, 'r') as f:
        ls = f.readlines()
        if len(ls) > 0:
            for i in ls:
                try:
                    clsnum = int(i.split(' ')[0])
                    dic[clsnum] += 1
                except:
                    pass
    # RES.append(FileCls(filename, dic))
    return FileCls(filename, dic)


@logit()
def split(folder: str, savaFolder: str, nc: int = 40, multiprocesses=True):
    global RES
    txts = glob.glob(folder + os.sep + "*.txt")
    if not len(txts) > 0:
        logger.error('Folder is empty, none txt file found!')
        return

    trainFile = open(savaFolder + os.sep + 'train.txt', 'w', encoding='utf-8')
    trainvalFile = open(savaFolder + os.sep + 'val.txt', 'w', encoding='utf-8')

    dic = dict()
    for k in range(0, nc):
        dic[k] = 0

    logger.info('======== start analysing ========')
    # for t in tqdm(txts):
    #     with open(t,'r') as ft:
    #         ls = ft.readlines()
    pool = Pool(__CPUS__ - 1)
    pool_list = []

    for t in txts:
        resultpool = pool.apply_async(getInfo, (t, dic))
        pool_list.append(resultpool)

    for pr in tqdm(pool_list):
        res = pr.get()  
        RES.append(res)
    
    

    # print(len(RES))
    s = RES[0]

    for i in RES[1:]:
        # print(i.clses)
        s += i
    
    print(s.clses)

