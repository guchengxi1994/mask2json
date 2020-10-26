'''
@lanhuage: python
@Descripttion: Deprecated.
@version: beta
@Author: xiaoshuyui
@Date: 2020-07-13 16:28:35
LastEditors: xiaoshuyui
LastEditTime: 2020-10-20 09:35:54
'''
import os
import shutil

FLAG = True
try:
    from labelme import utils
except ImportError:
    FLAG = False

if FLAG:
    pa = utils.__file__

    father_path = os.path.abspath(os.path.dirname(pa) + os.path.sep + ".")
    BASE_DIR = os.path.abspath(os.curdir)
    drawFile = BASE_DIR + os.sep + 'backup' + os.sep + 'draw.py'
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
