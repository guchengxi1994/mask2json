'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-07-13 16:43:58
LastEditors: xiaoshuyui
LastEditTime: 2021-01-05 11:16:24
'''
from convertmask import baseDecorate
import os
import shutil

from labelme import utils

pa = utils.__file__
father_path = os.path.abspath(os.path.dirname(pa) + os.path.sep + ".")

BASE_DIR = os.path.abspath(os.curdir)
drawFile = BASE_DIR + os.sep + 'draw.py'
# print(drawFile)

@baseDecorate()
def cp():
    # print(drawFile)
    if os.path.exists(father_path + os.sep + 'draw.py'):
        pass
    else:
        shutil.copy(drawFile, father_path + os.sep)
        f = open(pa, 'a')
        lis = [
            'from .draw import label_colormap',
            'from .draw import _validate_colormap',
            'from .draw import label2rgb', 'from .draw import draw_label',
            'from .draw import draw_instances'
        ]

        for i in lis:
            f.write(i + '\n')

        f.close()


def fileExist():
    # print(drawFile)
    if os.path.exists(father_path + os.sep + 'draw.py'):
        # pass
        return True
    else:
        return False
        # shutil.copy(drawFile,father_path+os.sep)
        # f = open(pa,'a')
        # lis = [
        #     'from .draw import label_colormap',
        #     'from .draw import _validate_colormap',
        #     'from .draw import label2rgb',
        #     'from .draw import draw_label',
        #     'from .draw import draw_instances'
        # ]

        # for i in lis:
        #     f.write(i+'\n')

        # f.close()
