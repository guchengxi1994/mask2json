'''convertmask

Usage:
    m2j_m.py    -h | --help
    m2j_m.py    -v | --version
    m2j_m.py    m2j
    m2j_m.py    m2x
    m2j_m.py    j2m
    m2j_m.py    j2x
    m2j_m.py    aug  [--nolabel]

options:
    -h --help   This script is used to convert mask files to xml/json files .
                Also, image augmentation and create corresponding xml/json files . 

    -v --version  show current version

                m2j     short for masks to jsons. 
                m2x     short for masks to xmls. 
                j2m     short for jsons to masks. 
                j2x     short for json to xml.
                aug     image augmentation. if [--nolabel] is provided,then json file path is not necessary

'''
import os
import sys

sys.path.append('..')

from docopt import docopt

from convertmask import __version__, baseDecorate
from convertmask.utils.backup.cpFile import fileExist
from convertmask.utils.imgAug_script import (imgAug_withLabels,
                                             imgAug_withoutLabels)
from convertmask.utils.json2mask.convert import processor
from convertmask.utils.json2xml.json2xml import j2xConvert
from convertmask.utils.mask2json_script import getJsons, getXmls
from convertmask.utils.methods.logger import logger

if not fileExist():
    logger.warning("connot find draw.py in labelme folder,which may cause some errors on labelme 4.2.9 (and maybe later). You can add it follow this step:https://github.com/guchengxi1994/mask2json#how-to-use")

class MethodNotSupportException(Exception):
    pass


@baseDecorate()
def script():
    arguments = docopt(__doc__)

    if arguments.get('--version') or arguments.get('-v'):
        print(__version__)

    elif arguments.get('m2j'):
        logger.info("Masks to jsons")
        print("<====  please input origin image path  ====>")
        inputOriimgPath = input()
        print("<====  please input mask path  ====>")
        inputMaskPath = input()

        if not os.path.exists(inputMaskPath):
            raise FileNotFoundError('mask folder is not exist')

        savePath = inputMaskPath
        print("<====  please input yaml path (can be blank,better dont) ====>")
        inputYamlPath = input()
        getJsons(inputOriimgPath,inputMaskPath,savePath,inputYamlPath)
        print("Done!")


    elif arguments.get('m2x'):
        logger.info("Masks to xmls")
        print("<====  please input origin image path  ====>")
        inputOriimgPath = input()
        print("<====  please input mask path  ====>")
        inputMaskPath = input()

        if not os.path.exists(inputMaskPath):
            raise FileNotFoundError('mask folder is not exist')

        savePath = inputMaskPath
        getXmls(inputOriimgPath,inputMaskPath,savePath)
        print("Done!")

    elif arguments.get('j2m'):
        logger.info("Jsons to masks")
        print("<====  please input json files path  ====>")
        inputJsonPath = input()
        processor(inputJsonPath)
        print('Done!')

    elif arguments.get('j2x'):
        logger.info("Json to xml (single file supported if version<=0.3)")
        print("<====  please input json file path  ====>")
        inputJsonPath = input()
        j2xConvert(inputJsonPath)
        print('Done!')

    elif arguments.get('aug'):
        # logger.info("Image augmentation (single file supported if version<=0.3)")
        if not arguments.get('--nolabel'):
            print("<====  please input image file path  ====>")
            inputFilePath = input()
            print("<====  please input json file path  ====>")
            inputJsonPath = input()
            imgAug_withLabels(inputFilePath,inputJsonPath)
        else:
            print("<====  please input image file path  ====>")
            inputFilePath = input()
            imgAug_withoutLabels(inputFilePath)







if __name__ == "__main__":
    script()
