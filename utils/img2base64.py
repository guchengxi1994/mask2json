'''
@lanhuage: python
@Descripttion: 
@version: beta
@Author: xiaoshuyui
@Date: 2020-06-09 16:25:31
@LastEditors: xiaoshuyui
@LastEditTime: 2020-06-10 09:06:50
'''
import base64
import _io

def imgEncode(img_or_path):
    if isinstance(img_or_path,str):
        i = open(img_or_path,'rb')
    elif isinstance(img_or_path,_io.BufferedReader):
        i = img_or_path
    else:
        raise TypeError('Input type error!')
    
    base64_data = base64.b64encode(i.read())

    return base64_data.decode()
