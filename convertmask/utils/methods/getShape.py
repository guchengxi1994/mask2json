'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-06-09 16:31:45
LastEditors: xiaoshuyui
LastEditTime: 2021-02-19 16:45:16
'''
import cv2
import numpy as np

# from .getArea import getAreaOfPolyGonbyVector

currentCV_version = cv2.__version__  #str


def get_approx(img, contour, length_p=0.1):
    """获取逼近多边形

    :param img: 处理图片
    :param contour: 连通域
    :param length_p: 逼近长度百分比
    """
    img_adp = img.copy()
    # 逼近长度计算
    epsilon = length_p * cv2.arcLength(contour, True)
    # 获取逼近多边形
    approx = cv2.approxPolyDP(contour, epsilon, True)

    return approx


def getBinary(img_or_path, minConnectedArea=20):
    if isinstance(img_or_path, str):
        i = cv2.imread(img_or_path)
    elif isinstance(img_or_path, np.ndarray):
        i = img_or_path
    else:
        raise TypeError('Input type error')

    if len(i.shape) == 3:
        img_gray = cv2.cvtColor(i, cv2.COLOR_BGR2GRAY)

    else:
        img_gray = i

    ret, img_bin = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY)

    _, labels, stats, centroids = cv2.connectedComponentsWithStats(img_bin)
    # print(stats.shape)
    for index in range(1, stats.shape[0]):
        if stats[index][4] < minConnectedArea or stats[index][4] < 0.1 * (
                stats[index][2] * stats[index][3]):
            labels[labels == index] = 0

    labels[labels != 0] = 1

    img_bin = np.array(img_bin * labels).astype(np.uint8)
    # print(img_bin.shape)

    return i, img_bin


def getRegion(img, img_bin):

    img_bin, contours, hierarchy = cv2.findContours(img_bin, cv2.RETR_LIST,
                                                    cv2.CHAIN_APPROX_SIMPLE)

    region = get_approx(img, contours[0], 0.002)
    return region


def getMultiRegion(img, img_bin):
    """
    for multiple objs in same class
    """
    # tmp = currentCV_version.split('.')
    if float(currentCV_version[0:3]) < 3.5:
        img_bin, contours, hierarchy = cv2.findContours(
            img_bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    else:
        contours, hierarchy = cv2.findContours(img_bin, cv2.RETR_LIST,
                                               cv2.CHAIN_APPROX_SIMPLE)
    # print(contours)
    # print(len(contours))
    regions = []
    if len(contours) >= 1:
        for i in range(0, len(contours)):
            if i != []:
                # print(len(contours[i]))
                region = get_approx(img, contours[i], 0.002)
                # print(region)
                if region.shape[0] > 3:
                    regions.append(region)

        return regions
    else:
        return []


def process(oriImg):
    img, img_bin = getBinary(oriImg)

    return getMultiRegion(img, img_bin)
