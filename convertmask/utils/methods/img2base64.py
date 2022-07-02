'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-06-09 16:25:31
LastEditors: xiaoshuyui
LastEditTime: 2021-02-19 16:44:38
'''
import base64
from convertmask import baseDecorate
# import cv2
import io

import numpy as np
import PIL


@baseDecorate()
def imgEncode(img_or_path):
    if isinstance(img_or_path, np.ndarray):
        """
        copy from labelme image.py    
        """
        img_pil = PIL.Image.fromarray(img_or_path)
        f = io.BytesIO()
        img_pil.save(f, format='PNG')
        img_bin = f.getvalue()
        if hasattr(base64, 'encodebytes'):
            img_b64 = base64.encodebytes(img_bin)
        else:
            img_b64 = base64.encodestring(img_bin)
        # _, enc = cv2.imencode('.jpg', img_or_path)
        # base64_data = base64.urlsafe_b64encode(enc.tobytes())
        return img_b64

    else:
        if isinstance(img_or_path, str):
            i = open(img_or_path, 'rb')
        elif isinstance(img_or_path, io.BufferedReader):
            i = img_or_path
        else:
            raise TypeError('Input type error!')

        base64_data = base64.b64encode(i.read())

        return base64_data.decode()


def img_data_to_arr(img_data):
    f = io.BytesIO()
    f.write(img_data)
    img_arr = np.array(PIL.Image.open(f))
    return img_arr


def img_b64_to_arr(img_b64):
    img_data = base64.b64decode(img_b64)
    img_arr = img_data_to_arr(img_data)
    return img_arr
