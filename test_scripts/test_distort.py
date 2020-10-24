'''
lanhuage: python
Descripttion:  https://www.pythonf.cn/read/138307 . test image distortion.
version: beta
Author: xiaoshuyui
Date: 2020-10-19 11:31:35
LastEditors: xiaoshuyui
LastEditTime: 2020-10-20 09:36:22
'''
import math
#读取图片
import random

import cv2
#为GS图像增加径向畸变
import numpy as np

img = cv2.imread(
    "D:\\testALg\\mask2json\\mask2json\\static\\multi_objs.jpg",
    1)  #cv2.IMREAD_UNCHANGED  D:\Microsoft internet download\left1\
print("{}".format(img.shape))
rows, cols, chn = img.shape

dst_img = np.zeros((rows, cols, chn))

#设置内参
fx = 2414.55  #779.423
fy = 2413.54  #779.423
cx = 1115.09  #450
cy = 814.736  #450

#径向畸变参数
# k1 = 0.274058
# k2 = -1.56158
# k3 = 2.86023

k1 = random.uniform(-1.0, 1.0)
k2 = random.uniform(-2.0, 2.0)
k3 = random.uniform(-1.0, 1.0)

for j in range(rows):
    for i in range(cols):
        #转到相机坐标系
        x = (i - cx) / fx
        y = (j - cy) / fy
        r = x * x + y * y

        #print("{}".format(r))

        #加入径向畸变
        newx = x * (1 + k1 * r + k2 * r * r + k3 * r * r * r)
        newy = y * (1 + k1 * r + k2 * r * r + k3 * r * r * r)

        #再转到图像坐标系
        u = newx * fx + cx
        v = newy * fy + cy

        #双线性插值
        u0 = math.floor(u)  #相当于上述公式中的x横坐标为0
        v0 = math.floor(v)  #相当于上述公式中的y纵坐标为0
        u1 = u0 + 1  #相当于上述公式中的x横坐标为1
        v1 = v0 + 1  #相当于上述公式中的y纵坐标为1

        dx = u - u0  #这里dx相当于上述公式中的x
        dy = v - v0  #这里dy相当于上述公式中的y
        weight1 = (1 - dx) * (1 - dy)
        weight2 = dx * (1 - dy)
        weight3 = (1 - dx) * dy
        weight4 = dx * dy

        if u0 >= 0 and u1 < cols and v0 >= 0 and v1 < rows:
            dst_img[j, i, :] = (1 - dx) * (1 - dy) * img[v0, u0, :] + (
                1 - dx) * dy * img[v1, u0, :] + dx * (
                    1 - dy) * img[v0, u1, :] + dx * dy * img[v1, u1, :]
cv2.imwrite("multi_objs_distort.jpg", dst_img)
