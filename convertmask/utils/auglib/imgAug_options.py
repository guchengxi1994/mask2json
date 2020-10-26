'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-10-26 10:14:35
LastEditors: xiaoshuyui
LastEditTime: 2020-10-26 11:34:08
'''
import os

import numpy as np
from convertmask.utils.auglib.optional.Operator import (CropOperator,
                                                        DistortOperator,
                                                        InpaintOperator,
                                                        PerspectiveOperator,
                                                        ResizeOperator)
from convertmask.utils.methods.logger import logger
from skimage import io


def aug(filepath: str,
        augs=['crop', 'distort', 'inpaint', 'perspective', 'resize']):
    l = np.random.randint(2, size=len(augs))
    if np.sum(l) == 0:
        l[0] = 1

    l = l.tolist()
    p = list(zip(augs, l))

    if isinstance(filepath, str) and os.path.exists(filepath):
        img = io.imread(filepath)
    elif isinstance(filepath, np.ndarray):
        img = filepath
    else:
        logger.error('File not found!')
        return

    for i in p:
        if i[1] == 1:
            if i[0] == 'crop':
                pass
