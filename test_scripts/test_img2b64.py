'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-10-10 09:37:10
LastEditors: xiaoshuyui
LastEditTime: 2020-10-10 15:39:02
'''
import sys
sys.path.append('..')
import os
from skimage import io
from convertmask.utils.methods.img2base64 import imgEncode
import json
try:
    from labelme import __version__
except:
    __version__ = '4.2.9'

BASE_DIR = os.path.abspath(os.path.dirname(os.getcwd())) + os.sep + 'static'
imgPath = BASE_DIR + os.sep + 'multi_objs_test.jpg'

if __name__ == "__main__":
    image = io.imread(imgPath)
    base64Code = imgEncode(image).decode()

    # print(base64Code)
    (fatherPath, filename_ext) = os.path.split(imgPath)
    (filename, _) = os.path.splitext(filename_ext)

    ob = dict()
    ob['imageData'] = base64Code
    ob['flags'] = {}
    ob['version'] = __version__
    ob['imagePath'] = filename_ext
    ob['shapes'] = []

    ob['imageHeight'] = image.shape[0]
    ob['imageWidth'] = image.shape[1]
    # ob['shapes'] = shapes

    with open(fatherPath + os.sep + filename + '.json', 'w',
              encoding='utf-8') as f:
        j = json.dumps(ob, sort_keys=True, indent=4)
        f.write(j)
    print('save to path {}'.format(fatherPath + os.sep + filename + '.json'))
