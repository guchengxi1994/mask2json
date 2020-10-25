<!--
 * @lanhuage: markdown
 * @Descripttion: 
 * @version: beta
 * @Author: xiaoshuyui
 * @Date: 2020-10-22 09:30:24
 * @LastEditors: xiaoshuyui
 * @LastEditTime: 2020-10-23 09:19:14
-->
# This function is used to convert xmls to jsons.

## This function just supports labelImg and [LabelImgTool](https://github.com/lzx1413/LabelImgTool).

## How to use.

    import os
    from convertmask.utils.xml2json.xml2json import getPolygon, x2jConvert, x2jConvert_pascal

    BASE_DIR = os.path.abspath(os.path.dirname(os.getcwd())) + os.sep + 'static'

    if __name__ == "__main__":
        x2jConvert(BASE_DIR + os.sep + 'bbox_label.xml',
                BASE_DIR + os.sep + 'bbox_label.jpg')

        x2jConvert_pascal(BASE_DIR + os.sep + 'bbox_label.xml',
                        BASE_DIR + os.sep + 'bbox_label.jpg')