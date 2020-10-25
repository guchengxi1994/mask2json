<!--
 * @lanhuage: markdown
 * @Descripttion: 
 * @version: beta
 * @Author: xiaoshuyui
 * @Date: 2020-10-22 09:31:00
 * @LastEditors: xiaoshuyui
 * @LastEditTime: 2020-10-23 09:25:12
-->
# This function is used to convert yolo to xmls.

### It is a reverse of 'xml2yolo'.

## How to use.

    import os
    from convertmask.utils.yolo2xml.yolo2xml import *

    BASE_DIR = os.path.abspath(os.path.dirname(
        os.getcwd())) + os.sep + 'static' + os.sep + 'yolo2xml' + os.sep

    if __name__ == "__main__":
        txtpath = BASE_DIR + 'test.txt'
        imgpath = BASE_DIR + 'test.jpg'
        labelPath = BASE_DIR + 'voc.names'
        y2xConvert(txtPath=txtpath,imgPath=imgpath,labelPath=labelPath)