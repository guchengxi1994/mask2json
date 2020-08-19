'''
@lanhuage: python
@Descripttion: 
@version: beta
@Author: xiaoshuyui
@Date: 2020-07-10 09:35:58
LastEditors: xiaoshuyui
LastEditTime: 2020-08-19 09:02:24
'''
import argparse
import os
import sys
sys.path.append('..')
from utils.getMultiShapes import getMultiShapes
from utils.cpFile import cp
from utils.convert import processor
# from utils.img2xml import processor_singleObj,processor_multiObj
# from mask2json import getJsons
from utils.mask2json_script import getJsons,getXmls
# import warnings
from utils.logger import logger
import configparser
cfp = configparser.ConfigParser()


BASE_DIR = os.path.abspath(os.curdir)
# print(BASE_DIR)
config_ROOT = BASE_DIR + os.sep  + 'config.ini'
cfp.read(config_ROOT)

default_yaml_path = cfp.get('default-yaml-path','path')

cp()

class MethodNotSupportException(Exception):
    pass

def test_json2mask():
    processor('../static/1-2cvt.json','gbk')

def script():
    parser = argparse.ArgumentParser(description='mask2json (labelme) /mask2xml (labelimg)',add_help=False)
    parser.add_argument('-help', action="help", help="This script is used to convert labeled imgs to json/xml files. \n  try:  \n  \
        convertmask --mode --in --out  \n \
             --mode ,now support  1) mask to json files(labelme) ; \n \
                                  2) mask to xml files(labelimg,support write xml files under this version) ; \n \
                                  3) json files to masks")
    # parser.add_argument('-f', '--foo')
    parser.add_argument('--mode',type=int,default=1,help="different mode params: [1,2,3]. 1:mask to json files \
                        2: mask to xml files,3:json files to masks")
    parser.add_argument('--input',type=str,help='input file path')
    parser.add_argument('--mask',type=str,help='input mask file path')
    parser.add_argument('--output',type=str,help='output file path')
    parser.add_argument('--encoding',type=str,default='utf-8',help="file encoding")
    parser.add_argument('--usecache',type=bool,default=True)
    args = parser.parse_args()
    # print(args.mode)
    if len(sys.argv) == 1 or (len(sys.argv)==2 and sys.argv[1] == '-help'):
        parser.print_help()
    else:
        if args.mode == 1:
            s = ''
            if not os.path.exists(default_yaml_path):
                logger.warning("Input the default yaml-path \n if not, the script is not tested")
            if not args.usecache:
                s = input()
            if s!= '' and s is not None and os.path.exists(s):
                cfp.set('default','path',s)
                with open(config_ROOT,'w+') as f:
                    cfp.write(f)
                getJsons(args.input,args.mask,args.output,s)
            else:
                getJsons(args.input,args.mask,args.output,default_yaml_path)
        elif args.mode == 2:
            # logger.warning("<===== this method is not tested =====>")
            getXmls(args.input,args.mask,args.output)
            # processor_singleObj.img2xml()
            # processor_multiObj.img2xml_multiobj()
            # raise MethodNotSupportException('Method not support yet')
        elif args.mode == 3:
            processor(args.input,args.encoding)
        else:
            raise MethodNotSupportException("no extra method supported yet")
        # if  args.input  and args.mode == 1:
        #     getJsons()
            
    
    


if __name__ == "__main__":
    # test_json2mask()
    script()