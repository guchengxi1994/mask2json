'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-11-24 13:28:51
LastEditors: xiaoshuyui
LastEditTime: 2020-11-24 13:40:42
'''
# -*- coding=utf-8 -*-
import glob
import os
import numpy as np
from kmeans import kmeans, avg_iou

# 根文件夹
ROOT_PATH = 'D:\\facedetect\\dump\\txts\\'
# 聚类的数目
CLUSTERS = 9
# 模型中图像的输入尺寸，默认是一样的
SIZE = 416

# 加载YOLO格式的标注数据
def load_dataset(path):
    # jpegimages = os.path.join(path, 'JPEGImages')
    # if not os.path.exists(jpegimages):
    #     print('no JPEGImages folders, program abort')
    #     sys.exit(0)
    # labels_txt = os.path.join(path, 'labels')
    # if not os.path.exists(labels_txt):
    #     print('no labels folders, program abort')
    #     sys.exit(0)

    label_file = glob.glob(path+'*.txt')
    print('label count: {}'.format(len(label_file)))
    dataset = []

    for label in label_file:
        with open(os.path.join( label), 'r') as f:
            txt_content = f.readlines()

        for line in txt_content:
            line_split = line.split(' ')
            roi_with = float(line_split[len(line_split)-2])
            roi_height = float(line_split[len(line_split)-1])
            if roi_with == 0 or roi_height == 0:
                continue
            dataset.append([roi_with, roi_height])
            # print([roi_with, roi_height])

    return np.array(dataset)

data = load_dataset(ROOT_PATH)
out = kmeans(data, k=CLUSTERS)

print(out)
print("Accuracy: {:.2f}%".format(avg_iou(data, out) * 100))
print("Boxes:\n {}-{}".format(out[:, 0] * SIZE, out[:, 1] * SIZE))

ratios = np.around(out[:, 0] / out[:, 1], decimals=2).tolist()
print("Ratios:\n {}".format(sorted(ratios)))
