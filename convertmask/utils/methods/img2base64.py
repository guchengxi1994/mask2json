'''
@lanhuage: python
@Descripttion: 
@version: beta
@Author: xiaoshuyui
@Date: 2020-06-09 16:25:31
LastEditors: xiaoshuyui
LastEditTime: 2020-10-10 09:34:55
'''
import base64
import _io
import numpy as np
# import cv2
import io
import PIL

def imgEncode(img_or_path):
    if isinstance(img_or_path,np.ndarray):
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
        if isinstance(img_or_path,str):
            i = open(img_or_path,'rb')
        elif isinstance(img_or_path,_io.BufferedReader):
            i = img_or_path
        else:
            raise TypeError('Input type error!')
        
        base64_data = base64.b64encode(i.read())

        return base64_data.decode()
