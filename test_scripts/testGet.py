'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2021-01-14 16:21:31
LastEditors: xiaoshuyui
LastEditTime: 2021-01-14 17:30:54
'''

"""
{0: 0, 1: 0, 2: 0, 3: 1, 4: 33, 5: 1, 6: 14, 7: 19, 8: 0, 9: 0, 10: 0, 11: 0, 12: 33, 13: 0, 14: 0, 15: 0, 16: 34, 17: 0, 18: 1, 19: 0, 20: 0, 21: 0, 22: 3, 23: 65, 24: 0, 25: 0, 26: 136, 27: 113, 28: 143, 29: 39, 30: 80, 31: 41, 32: 39, 33: 22, 34: 34, 35: 39, 36: 13, 37: 9, 38: 34, 39: 0, 40: 0, 41: 37}
{0: 0, 1: 0, 2: 0, 3: 0, 4: 8, 5: 0, 6: 4, 7: 4, 8: 0, 9: 0, 10: 0, 11: 0, 12: 4, 13: 0, 14: 0, 15: 0, 16: 8, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 16, 24: 0, 25: 0, 26: 24, 27: 24, 28: 28, 29: 8, 30: 16, 31: 8, 32: 4, 33: 0, 34: 8, 35: 8, 36: 4, 37: 0, 38: 4, 39: 0, 40: 0, 41: 8}
"""

"""
D:\112\test\cutImg506x2.txt
D:\112\test\cutImg51x2.txt
D:\112\test\cutImg514x3.txt
"""

import sys
sys.path.append('..')

from convertmask.utils.train_val_dataset_split.yololike import getInfo, getSum


with open('D:\\testALg\\mask2json\\mask2json\\test_scripts\\DevLog\\val.txt') as f:
    res = f.readlines()




RES = []

for ii in res:
    dic = dict()
    for k in range(0, 42):
        dic[k] = 0
    pr = getInfo(ii.replace('\n',''),dic)
    print(pr.filename)
    print(pr.clses)
    RES.append(pr)

# tmp = getSum(RES)
# print(tmp.clses)

print("&&&"*60)

tmp = RES[0]
for ii in range(1,len(RES)):
    print(RES[ii].filename)
    print(RES[ii].clses)
    tmp = tmp + RES[ii]

print(tmp.clses)



