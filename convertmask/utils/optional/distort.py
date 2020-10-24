'''
lanhuage: python
Descripttion: modified from https://github.com/cedricporter/EffectLab/blob/master/EffectLab/Effect.py
version: beta
Author: xiaoshuyui
Date: 2020-10-23 13:18:56
LastEditors: xiaoshuyui
LastEditTime: 2020-10-23 13:49:44
'''
import operator
import os
import random
from math import sqrt

import numpy as np
from convertmask.utils.methods.logger import logger
from PIL import Image
from skimage import io


def _div(t: list, v):
    tmp = np.array(t)
    tmp = tmp / v
    return tmp.astype(np.uint8).tolist()


def warp(x, y, r, center: tuple = None, mouse: tuple = None):
    if center is None:
        center = (130, 120)
    if mouse is None:
        mouse = (130, 50)
    cx, cy = center
    mx, my = mouse

    dis_x_c = sqrt((x - cx)**2 + (y - cy)**2)
    dis_m_c = sqrt((x - mx)**2 + (y - my)**2)

    div = float(r**2 - dis_x_c**2 + dis_m_c**2)
    if div == 0:
        div = 0.0000000001
    factor = ((r**2 - dis_x_c**2) / div)**2

    u = x - factor * (mx - cx)
    v = y - factor * (my - cy)

    return u, v


def imgFilter(img: Image,
              radius: int = 100,
              center: tuple = None,
              mouse: tuple = None,
              antialias=2):
    width, height = img.size
    new_img = img.copy()
    r = radius

    if center is None:
        center = (130, 120)
    if mouse is None:
        mouse = (130, 50)

    cx, cy = center
    mx, my = mouse

    nband = len(img.getpixel((0, 0)))
    antialias = antialias

    for x in range(width):
        for y in range(height):
            if sqrt((x - cx)**2 + (y - cy)**2) > r:
                continue

            found = 0
            psum = (0, ) * nband

            # anti-alias
            for ai in range(antialias):
                _x = x + ai / float(antialias)
                for aj in range(antialias):
                    _y = y + aj / float(antialias)
                    u, v = warp(_x, _y, r, (cx, cy), (mx, my))
                    u = int(round(u))
                    v = int(round(v))
                    if not (0 <= u < width and 0 <= v < height):
                        continue
                    pt = img.getpixel((u, v))
                    psum = map(operator.add, psum, pt)
                    found += 1

            if found > 0:
                psum = _div(list(psum), found)
                new_img.putpixel((x, y), tuple(psum))

    return new_img


def imgDistort(filepath: str, flag=True):
    if isinstance(filepath, str):
        if os.path.exists(filepath):
            img = io.imread(filepath)
        else:
            raise FileNotFoundError('Image file not found!')
    elif isinstance(filepath, np.ndarray):
        img = filepath
    else:
        logger.error('Input file error')
        return

    imgShape = img.shape
    imgWidth = imgShape[1]
    imgHeight = imgShape[0]

    center = (random.randint(int(0.2 * imgWidth), int(0.8 * imgWidth)),
              random.randint(int(0.2 * imgHeight), int(0.8 * imgHeight)))
    mouse = (random.randint(int(0.2 * imgWidth), int(0.8 * imgWidth)),
             random.randint(int(0.2 * imgHeight), int(0.8 * imgHeight)))
    radious = random.randint(50, 250)

    input_img = Image.fromarray(img).convert('RGB')

    resImg = imgFilter(input_img, radious, center, mouse)
    resImg = np.array(resImg)

    if flag:
        image_path, _ = os.path.splitext(filepath)
        io.imsave(image_path + '_distort.jpg', resImg)
        logger.info('Saved to {}'.format(image_path + '_distort.jpg'))
    else:
        return resImg
