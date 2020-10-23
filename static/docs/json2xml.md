<!--
 * @lanhuage: markdown
 * @Descripttion: 
 * @version: beta
 * @Author: xiaoshuyui
 * @Date: 2020-10-22 09:29:52
 * @LastEditors: xiaoshuyui
 * @LastEditTime: 2020-10-23 09:10:21
-->
# This function is used to convert jsons to xmls.

## How to use.

    import os
    from convertmask.utils.json2xml.json2xml import j2xConvert

    BASE_DIR = os.path.abspath(os.path.dirname(os.getcwd())) + os.sep + 'static'
    j2xConvert(BASE_DIR + '/label_255_p.json')

It is a simple function.