<!--
 * @lanhuage: markdown
 * @Descripttion: 
 * @version: beta
 * @Author: xiaoshuyui
 * @Date: 2020-10-22 09:30:49
 * @LastEditors: xiaoshuyui
 * @LastEditTime: 2020-10-23 09:24:17
-->
# This function is used to convert xmls(pascal) to yolo.

# How to use.

    from convertmask.utils.xml2yolo.xml2yolo import x2yConvert
    import os

    BASE_DIR = os.path.abspath(os.path.dirname(
        os.getcwd())) + os.sep + 'static' + os.sep + 'test_xmls'

    if __name__ == "__main__":
        # single file test
        sfile = BASE_DIR + os.sep + '1187_3.xml'
        x2yConvert(sfile)

        # multi file test
        x2yConvert(BASE_DIR + os.sep + 'xmls')

It is a eazy function.