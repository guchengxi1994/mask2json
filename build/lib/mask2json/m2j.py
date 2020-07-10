'''
@lanhuage: python
@Descripttion: 
@version: beta
@Author: xiaoshuyui
@Date: 2020-07-10 09:35:58
@LastEditors: xiaoshuyui
@LastEditTime: 2020-07-10 13:29:32
'''
import argparse
import sys
sys.path.append('..')
from utils.getMultiShapes import getMultiShapes
from utils.convert import processor
from utils.img2xml import processor_singleObj
# from mask2json import getJsons
from utils.mask2json_script import getJsons

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
    args = parser.parse_args()
    # print(args.mode)
    if len(sys.argv) == 1 or (len(sys.argv)==2 and sys.argv[1] == '-help'):
        parser.print_help()
    else:
        if args.mode == 1:
            getJsons(args.input,args.mask,args.output)
        elif args.mode == 2:
            # processor_singleObj.img2xml()
            raise MethodNotSupportException('Method not support yet')
        elif args.mode == 3:
            processor(args.input,args.encoding)
        else:
            raise MethodNotSupportException("no extra method supported yet")
        # if  args.input  and args.mode == 1:
        #     getJsons()
            
    
    


if __name__ == "__main__":
    # test_json2mask()
    script()