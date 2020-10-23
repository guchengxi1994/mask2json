'''
lanhuage: python
Descripttion:  https://github.com/cedricporter/EffectLab/blob/master/EffectLab/Effect.py
version: beta
Author: xiaoshuyui
Date: 2020-10-23 11:03:38
LastEditors: xiaoshuyui
LastEditTime: 2020-10-23 13:44:42
'''
from math import sqrt
from PIL import Image
import operator
import numpy as np


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


def _div(t: list, v):
    tmp = np.array(t)
    tmp = tmp / v
    return tmp.astype(np.uint8).tolist()


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
                # print((found, ) * len(list(psum)))
                psum = _div(list(psum), found)
                # print(psum)
                # psum = map(operator.truediv, list(psum), (found, ) * len(list(psum)))
                new_img.putpixel((x, y), tuple(psum))

    return new_img


if __name__ == "__main__":
    # img = Image.open(
    #     "D:\\testALg\\mask2json\\mask2json\\static\\multi_objs.jpg")
    # res = imgFilter(img)

    # res.save("D:\\testALg\\mask2json\\mask2json\\static\\multi_objs_wrap.jpg")
    import sys
    sys.path.append('..')
    from convertmask.utils.optional.distort import imgDistort

    img = "D:\\testALg\\mask2json\\mask2json\\static\\multi_objs.jpg"

    imgDistort(img)