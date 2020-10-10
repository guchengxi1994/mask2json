'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-08-17 13:48:46
LastEditors: xiaoshuyui
LastEditTime: 2020-10-10 15:41:28
'''


def getAreaOfPolyGonbyVector(points):
    # 基于向量叉乘计算多边形面积
    area = 0
    if (len(points) < 3):

        raise Exception("points is not enough to calculate area!")

    for i in range(0, len(points) - 1):
        p1 = points[i]
        # print(p1)
        p2 = points[i + 1]

        triArea = (p1[0][0] * p2[0][1] - p2[0][0] * p1[0][1]) / 2
        area += triArea
    return abs(area)