'''
@lanhuage: python
@Descripttion: 
@version: beta
@Author: xiaoshuyui
@Date: 2020-06-10 09:20:18
LastEditors: xiaoshuyui
LastEditTime: 2021-01-04 13:56:17
'''


def rm(filepath):
    p = open(filepath, 'r+')

    lines = p.readlines()

    d = ""
    for line in lines:
        c = line.replace('"group_id": "null",', '"group_id": null,')
        d += c

    p.seek(0)
    p.truncate()
    p.write(d)
    p.close()