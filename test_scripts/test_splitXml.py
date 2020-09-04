'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-09-03 14:17:43
LastEditors: xiaoshuyui
LastEditTime: 2020-09-04 14:07:24
'''
import sys
sys.path.append("..")
import os
import glob

from convertmask.utils.longImgSplit import script as sc
save_dir = os.path.abspath(os.path.dirname(os.getcwd())) +os.sep + 'static'+os.sep+"testXmlSplit"+os.sep

if __name__ == "__main__":
    # sc.convertImgSplit(save_dir+'1.jpg',save_dir+'1.xml',yamlPath=save_dir+'info2.yaml')

    imgPath = 'D:\\1\\test\\'
    xmlPath = 'D:\\1\\testXml\\'

    xmls = glob.glob(xmlPath+os.sep+'*.xml')
    imgs = glob.glob(imgPath+os.sep+'*.jpg')

    for i in xmls:
        imgName = i.split(os.sep)[-1][:-4]

        img = imgPath+os.sep+imgName+".jpg"

        sc.convertImgSplit(img,i,yamlPath=save_dir+'info2.yaml')

        
    