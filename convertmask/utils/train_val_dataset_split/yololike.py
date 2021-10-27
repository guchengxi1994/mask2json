'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2021-01-13 13:42:14
LastEditors: xiaoshuyui
LastEditTime: 2021-02-19 16:42:15
'''
import glob
import os
from multiprocessing import Pool

from convertmask import __CPUS__
from convertmask.utils.methods.logger import logger
from tqdm import tqdm

from random import sample
import copy

RES = []
valList = []


class FileCls:
    def __init__(self, filename: str, clses: dict) -> None:
        self.filename = filename
        self.clses = clses

    def get(self, k):
        return self.clses.get(k, 0)

    def __add__(self, o):
        if not isinstance(o, self.__class__):
            return self
        nc = len(self.clses)
        dic = dict()
        for k in range(0, nc):
            dic[k] = 0
        c = FileCls('', dic)
        for i in range(0, nc):
            sn = self.get(i)
            on = o.get(i)
            c.clses[i] = sn + on
        return c

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, self.__class__):
            return False
        return self.filename == o.filename

    def __hash__(self) -> int:
        return hash(self.filename)


def getInfo(filename: str, dic: dict):
    with open(filename, 'r') as f:
        ls = f.readlines()
        if len(ls) > 0:
            for i in ls:
                try:
                    clsnum = int(i.split(' ')[0])
                    dic[clsnum] += 1
                except:
                    pass
    return FileCls(filename, dic)


def getSum(res: list):
    if len(res) > 1:
        s = res[0]
        for i in range(1, len(res)):
            s = s + res[i]
        return s
    elif len(res) == 1:
        return res[0]
    else:
        return None


def getMean(s: FileCls, nc: int, times: int = 10):
    data = s.clses
    res = []

    for i in range(0, nc):
        num = data.get(i, 0)
        if num <= 1:
            num = 0
        elif num <= times:
            num = 1
        else:
            num = round(1 / times * num)
        res.append([i, num])
    res.sort(key=lambda x: x[0])

    return res


def getTrainValSet(resList: list, r: list):
    global valList
    restRES = copy.deepcopy(resList)
    i = 0
    while i < len(r):
        if r[i][1] > 0:
            lis = list(filter(lambda x: x.clses.get(r[i][0], 0) > 0, restRES))
            thisValList = sample(lis, k=r[i][1])
            data = getSum(thisValList)
            for j in range(0, len(data.clses)):
                r[j][1] -= data.clses.get(j, 0)

            thisTrainList = list(set(lis).difference(set(thisValList)))

            restRES = list(set(restRES).difference(set(thisValList)))

            valList.extend(thisValList)
            thisValList.clear()
        i += 1


def split(folder: str, savaFolder: str, nc: int = 42, multiprocesses=True):
    global RES
    txts = glob.glob(folder + os.sep + "*.txt")
    if not len(txts) > 0:
        logger.error('Folder is empty, none txt file found!')
        return

    trainFile = open(savaFolder + os.sep + 'train.txt', 'w+', encoding='utf-8')
    trainvalFile = open(savaFolder + os.sep + 'val.txt',
                        'w+',
                        encoding='utf-8')

    logger.info('======== start analysing ========')
    pool = Pool(__CPUS__ - 1)
    pool_list = []

    for t in txts:
        dic = dict()
        for k in range(0, nc):
            dic[k] = 0
        resultpool = pool.apply_async(getInfo, (t, dic))
        pool_list.append(resultpool)

    for pr in tqdm(pool_list):
        res = pr.get()
        RES.append(res)

    tmp = getSum(RES)
    r = getMean(tmp, nc)

    getTrainValSet(RES, r)
    global valList

    for i in list(set(valList)):
        trainvalFile.write(i.filename + '\n')
    trainList = list(set(RES).difference(set(valList)))

    for i in trainList:
        trainFile.write(i.filename + '\n')

    trainvalFile.close()
    trainFile.close()
