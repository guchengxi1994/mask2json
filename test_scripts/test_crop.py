'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-10-23 17:14:44
LastEditors: xiaoshuyui
LastEditTime: 2020-10-23 17:53:53
'''
import sys
sys.path.append("..")
from convertmask.utils.optional.generatePolygon import generatePolygon
from skimage import io

if __name__ == "__main__":
    mask = generatePolygon((500,500,3),convexHull=True)
    io.imsave('D:\\testALg\\mask2json\\mask2json\\static\\augimgs_\\test.jpg',mask,convexHull=True)