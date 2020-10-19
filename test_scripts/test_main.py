#coding=utf-8
'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-10-16 11:06:01
LastEditors: xiaoshuyui
LastEditTime: 2020-10-19 10:42:14
'''
import sys
sys.path.append("..")
import os
BASE_DIR = os.path.abspath(os.path.dirname(os.getcwd()))

import convertmask.main_v_0_5_any as mainScript
from convertmask.utils.methods.logger import logger

mainScriptPath = mainScript.__file__
# print (mainScriptPath)

if __name__ == "__main__":
    logger.info('1.version')
    code = 'python {} -v'.format(mainScriptPath)
    os.system(code)

    logger.info('2.no inout')
    code = 'python {} '.format(mainScriptPath)
    os.system(code)

    logger.info('3.random method')
    code = 'python {} ma'.format(mainScriptPath)
    os.system(code)
    code = 'python {} mask2json -H'.format(mainScriptPath)
    os.system(code)

    logger.info('4.mask2json')
    oriImgPath = BASE_DIR + '/static/multi_objs.jpg'
    label_img = BASE_DIR + '/multi_objs_json/label.png'
    labelPath = BASE_DIR + '/multi_objs_json/info.yaml'

    code = 'python {} mask2json -i {}  {}  {}'.format(mainScriptPath,
                                                      oriImgPath, label_img,
                                                      labelPath)

    os.system(code)

    logger.info('5.mask2xml')
    oriImgPath = BASE_DIR + '/static/multi_objs.jpg'
    label_img = BASE_DIR + '/multi_objs_json/label.png'

    code = 'python {} mask2xml -i {}  {} '.format(mainScriptPath, oriImgPath,
                                                  label_img)

    os.system(code)

    logger.info('6.json2xml')
    oriImgPath = BASE_DIR + '/static/jsons_/multi_objs_rotation.json'
    code = 'python {} json2xml -i {}   '.format(mainScriptPath, oriImgPath)

    os.system(code)

    logger.info('7.json2mask')
    oriImgPath = BASE_DIR + '/static/multi_objs_sameclass.json'
    code = 'python {} json2mask -i {}   '.format(mainScriptPath, oriImgPath)

    os.system(code)

    logger.info('8.augmentation')
    oriImgPath1 = BASE_DIR + '/static/multi_objs.jpg'
    labelPath1 = BASE_DIR + '/static/multi_objs.json'

    oriImgPath2 = BASE_DIR + '/static/label_255.png'
    labelPath2 = BASE_DIR + '/static/label_255.xml'

    code = 'python {} augmentation -i {}  {} -N 2'.format(
        mainScriptPath, oriImgPath1, labelPath1)
    os.system(code)

    code = 'python {} augmentation -i {} {} -N 20 --labelImg'.format(
        mainScriptPath, oriImgPath2, labelPath2)
    os.system(code)

    logger.info('9.simplified test')
    oriImgPath1 = BASE_DIR + '/static/multi_objs.jpg'
    labelPath1 = BASE_DIR + '/static/multi_objs.json'

    oriImgPath2 = BASE_DIR + '/static/label_255.png'
    labelPath2 = BASE_DIR + '/static/label_255.xml'

    code = 'python {} aug -i {}  {} -N 2'.format(mainScriptPath, oriImgPath1,
                                                 labelPath1)
    os.system(code)

    code = 'python {} aug -i {} {} -N 20 --labelImg'.format(
        mainScriptPath, oriImgPath2, labelPath2)
    os.system(code)
