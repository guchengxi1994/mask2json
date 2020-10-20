'''
lanhuage: python
Descripttion: test split long images to sub images and generate label files.
version: beta
Author: xiaoshuyui
Date: 2020-09-03 14:17:43
LastEditors: xiaoshuyui
LastEditTime: 2020-10-20 09:47:32
'''
import sys
sys.path.append("..")
import os
import glob

from convertmask.utils.longImgSplit import script as sc
save_dir = os.path.abspath(os.path.dirname(
    os.getcwd())) + os.sep + 'static' + os.sep + "testXmlSplit" + os.sep

if __name__ == "__main__":
    # sc.convertImgSplit(save_dir+'1.jpg',save_dir+'1.xml',yamlPath=save_dir+'info2.yaml')

    imgPath = 'D:\\907\\imgs\\rename\\'
    xmlPath = 'D:\\907\\f\\'

    xmls = glob.glob(xmlPath + os.sep + '*.xml')
    imgs = glob.glob(imgPath + os.sep + '*.jpg')

    for i in xmls:
        imgName = i.split(os.sep)[-1][:-4]

        img = imgPath + os.sep + imgName + ".jpg"

        sc.convertImgSplit(img, i, yamlPath=save_dir + 'info2.yaml', bias=2000)
