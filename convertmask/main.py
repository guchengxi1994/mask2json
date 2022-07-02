'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-10-15 08:17:08
LastEditors: xiaoshuyui
LastEditTime: 2020-10-23 09:39:00
'''
import sys

sys.path.append('..')
import difflib
import os

import convertmask.utils.methods.config_utils as ccfg
from convertmask import (BaseParser, __appname__, __support_methods__,
                         __support_methods_simplified__)
from convertmask.utils.img_augment_script import (imgAug_LabelImg,
                                             imgAug_withLabels,
                                             imgAug_withoutLabels)
from convertmask.utils.json2mask.convert import processor
from convertmask.utils.json2xml.json2xml import j2xConvert
from convertmask.utils.mask2json_script import getJsons, getXmls
from convertmask.utils.methods.logger import logger
from convertmask.utils.xml2json.xml2json import x2jConvert, x2jConvert_pascal
from convertmask.utils.xml2yolo.xml2yolo import x2yConvert
from convertmask.utils.yolo2xml.yolo2xml import y2xConvert

ccfg.setConfigParam(ccfg.cfp, 'log', 'show', 'True')

supported_simplified_methods = __support_methods_simplified__.values()


def getKV(dic: dict):
    res = []
    for k, v in dic.items():
        res.append('{}({})'.format(v, k))

    return res


class MethodInputException(Exception):
    pass


class Parser(BaseParser):
    def __init__(self, args, appname):
        super().__init__(args, appname)
        self.args = args
        self.parser = super().get_parser()
        self.appname = appname

    def get_parser(self):
        self.parser.add_argument(
            'method',
            metavar='PROCESS_METHOD',
            type=str,
            nargs='?',
            help='the method to be processed. currently, {} are supported.'.
            format(','.join(__support_methods__)))

        self.parser.add_argument('-v',
                                 '--version',
                                 help='show current version',
                                 action='store_true')

        self.parser.add_argument('-i',
                                 '--input',
                                 type=str,
                                 nargs='*',
                                 help='input files')

        if len(self.args) > 0:
            for i in self.args:
                self.add_parser(i)
        else:
            logger.warning('args list is null')

        return self.parser

    def add_parser(self, arg):
        if type(arg) is tuple:
            self.parser.add_argument(arg[0],
                                     arg[1],
                                     help=arg[2],
                                     action='store_true')
        elif type(arg) is dict:
            # pass
            self.parser.add_argument(
                arg['shortName'],
                arg['fullName'],
                type=arg['type'],
                help=arg['help'],
            )
        else:
            raise TypeError('input argument type error')


def script():
    """
    eg. argList = [('-l', '--labels', 'label files path','store_true')]

    """
    argList = [
        ('-n', '--nolabel', 'image augmentation without labels'),
        ('-H', '--HELP',
         'show specific help informaton about supported method'),
        ('-X', '--labelImg',
         'image augmentation for labelImg, default labelme. "X" for xml'),
        # ('--number', 'image augmentation numbers, default 1'),
        {
            'shortName': '-N',
            'fullName': '--number',
            'type': int,
            'help': 'image augmentation numbers, default 1'
        },
        ('-L', '--nolog', 'remove "annoying" logs'),
        {
            'shortName':
            '-c',
            'fullName':
            '--classfilepath',
            'type':
            str,
            'help':
            'class-information-path(for labelme is a *.yaml file,for labelImg is a *.txt file. without this file, this script has some errors when generate mask files and image augumentation.)'
        }
    ]

    p = Parser(argList, __appname__)
    parser = p.get_parser()
    args = vars(parser.parse_args())

    # print(args)
    if args['version']:
        # print(1)
        from convertmask import __version__
        print(__version__)
        del __version__
        return

    if not args['method'] and not args['version']:
        parser.print_help()
        return

    if args['method'] and not args['input'] and not args['HELP']:
        logger.error('<=== INPUT FOLDER/FILE MUST NOT BE NULL ===>')
        return

    if args['nolog']:
        ccfg.setConfigParam(ccfg.cfp, 'log', 'show', 'False')

    if args['method'] not in __support_methods__ and args[
            'method'] not in supported_simplified_methods:
        # print(args['method'])
        kvs = getKV(__support_methods_simplified__)
        logger.warning(' only ==>{}  are supported'.format('\n==>'.join(kvs)))
        lis = difflib.get_close_matches(args['method'], __support_methods__)
        # print(lis)
        if len(lis) > 0:
            logger.info('do you mean: {} ?'.format(' OR '.join(lis)))
            del lis
            return

    if args['method'] == 'mask2json' or args[
            'method'] == __support_methods_simplified__['mask2json']:
        if args['HELP']:
            print('\n')
            print("<==== {} detailed information ====>".format(args['method']))
            print('\n')
            print('This method parameter list should follow this order.')
            print(
                '    origin-image-path(necessary), mask-image-path(necessary), yaml-file-path(can be blank,better dont)'
            )
            print(
                '    origin images are used to generate base64 code. mask images are used to generate polygons. yaml file saves classes information'
            )
            print('\n')
            print('<==== The End ====>')
            print('\n')
        else:
            params = args['input']
            if len(params) < 2:
                raise MethodInputException('Not enough input parameters')
            elif len(params) == 2:
                inputOriimgPath = params[0]
                inputMaskPath = params[1]
                savePath = os.path.dirname(inputMaskPath)
                inputYamlPath = ''
            elif len(params) == 3:
                inputOriimgPath = params[0]
                inputMaskPath = params[1]
                savePath = os.path.dirname(inputMaskPath)
                inputYamlPath = params[2]
            else:
                raise MethodInputException('Too much input parameters')

            getJsons(inputOriimgPath, inputMaskPath, savePath, inputYamlPath)
            print('Done!')

    if args['method'] == 'mask2xml' or args[
            'method'] == __support_methods_simplified__['mask2xml']:
        if args['HELP']:
            print('\n')
            print("<==== {} detailed information ====>".format(args['method']))
            print('\n')
            print('This method parameter list should follow this order.')
            print(
                '    origin-image-path(necessary), mask-image-path(necessary)')
            print('\n')
            print('<==== The End ====>')
            print('\n')
        else:
            params = args['input']
            if len(params) < 2:
                raise MethodInputException('Not enough input parameters')
            elif len(params) == 2:
                inputOriimgPath = params[0]
                inputMaskPath = params[1]
                savePath = os.path.dirname(inputMaskPath)
            else:
                raise MethodInputException('Too much input parameters')

            getXmls(inputOriimgPath, inputMaskPath, savePath)
            print('Done!')

    if args['method'] == 'json2xml' or args[
            'method'] == __support_methods_simplified__['json2xml']:
        if args['HELP']:
            print('\n')
            print("<==== {} detailed information ====>".format(args['method']))
            print('\n')
            print('This method parameter list should follow this order.')
            print('    json-file-path(necessary)')
            print('\n')
            print('<==== The End ====>')
            print('\n')
        else:
            params = args['input']
            if len(params) < 1:
                raise MethodInputException('Not enough input parameters')
            elif len(params) == 1:
                inputJsonPath = params[0]

            else:
                raise MethodInputException('Too much input parameters')

            j2xConvert(inputJsonPath)
            print('Done!')

    if args['method'] == 'json2mask' or args[
            'method'] == __support_methods_simplified__['json2mask']:
        if args['HELP']:
            print('\n')
            print("<==== {} detailed information ====>".format(args['method']))
            print('\n')
            print('This method parameter list should follow this order.')
            print('    json-file-path(necessary)')
            print('\n')
            print('<==== The End ====>')
            print('\n')
        else:
            params = args['input']
            if len(params) < 1:
                raise MethodInputException('Not enough input parameters')
            elif len(params) == 1:
                inputJsonPath = params[0]

            else:
                raise MethodInputException('Too much input parameters')

            processor(inputJsonPath)
            print('Done!')

    if args['method'] == 'augmentation' or args[
            'method'] == __support_methods_simplified__['augmentation']:
        if not args['number']:
            number = 1
        else:
            number = args['number']
        if args['HELP']:
            print('\n')
            print("<==== {} detailed information ====>".format(args['method']))
            print('\n')
            print('This method parameter list should follow this order.')
            print(
                '    origin-image-path(necessary), label-file-path(alternative).'
            )
            print('    --nolabel can be added to just augment images.')
            print(
                '    --labelImg can be added to augment xmls, default jsons.')
            print('\n')
            print('<==== The End ====>')
            print('\n')
        else:
            params = args['input']
            if args['classfilepath']:
                classFilePath = args['classfilepath']
            else:
                classFilePath = ''
            if len(params) < 1:
                raise MethodInputException('Not enough input parameters')
            elif len(params) == 1 and args['nolabel']:
                inputFilePath = params[0]
                imgAug_withoutLabels(inputFilePath, number)
                print('Done!')

            elif len(params) == 2:
                inputFilePath = params[0]
                inputJsonPath = params[1]
                if not args['labelImg']:
                    imgAug_withLabels(inputFilePath,
                                      inputJsonPath,
                                      number,
                                      yamlFilePath=classFilePath)
                else:
                    imgAug_LabelImg(inputFilePath,
                                    inputJsonPath,
                                    number)
                print('Done!')
            else:
                raise MethodInputException('There must be some errors.')

    if args['method'] == 'xml2json' or args[
            'method'] == __support_methods_simplified__['xml2json']:
        logger.info('<===  This is a test function.  ===>')
        if args['HELP']:
            print('\n')
            print("<==== {} detailed information ====>".format(args['method']))
            print('\n')
            print('This method parameter list should follow this order.')
            print('    xml-file-path(necessary), origin-image-path(necessary)')
            print('    currently, only single file conversion supported.')
            print(
                '    --labelImg can be added which means xmls are generated by labelImg.'
            )
            print('\n')
            print('<==== The End ====>')
            print('\n')
        else:
            params = args['input']
            if len(params) < 2:
                raise MethodInputException('Not enough input parameters')
            elif len(params) == 2:
                inputFilePath = params[0]
                inputJsonPath = params[1]
                if not args['labelImg']:
                    x2jConvert(inputFilePath, inputJsonPath)
                else:
                    x2jConvert_pascal(inputFilePath, inputJsonPath)
                print('Done!')
            else:
                raise MethodInputException('Too much input parameters')

    if args['method'] == 'yolo2xml' or args[
            'method'] == __support_methods_simplified__['yolo2xml']:
        if args['HELP']:
            print('\n')
            print("<==== {} detailed information ====>".format(args['method']))
            print('\n')
            print('This method parameter list should follow this order.')
            print(
                '    txt-file-path(necessary), origin-image-path(necessary), class-file-path(necessary'
            )
            print('    currently, only single file conversion supported.')
            print('\n')
            print('<==== The End ====>')
            print('\n')
        else:
            params = args['input']
            if len(params) < 3:
                raise MethodInputException('Not enough input parameters')
            elif len(params) == 3:
                txtpath = params[0]
                imgpath = params[1]
                labelPath = params[2]

            else:
                raise MethodInputException('Too much input parameters')

            y2xConvert(txtPath=txtpath, imgPath=imgpath, labelPath=labelPath)
            print('Done!')

    if args['method'] == 'xml2yolo' or args[
            'method'] == __support_methods_simplified__['xml2yolo']:
        if args['HELP']:
            print('\n')
            print("<==== {} detailed information ====>".format(args['method']))
            print('\n')
            print('This method parameter list should follow this order.')
            print('    xml-file-path(necessary), class-file-path(alternative)')
            print(
                '    class-file is a txt file saves class information. without this file, a txt file will be generated automaticly, which may be in different orders'
            )
            print('\n')
            print('<==== The End ====>')
            print('\n')
        else:
            params = args['input']
            if len(params) < 1:
                raise MethodInputException('Not enough input parameters')
            elif len(params) == 1:
                xmlpath = params[0]
                x2yConvert(xmlpath)
                print('Done!')
            elif len(params) == 2:
                xmlpath = params[0]
                labelpath = params[1]
                x2yConvert(xmlpath, labelpath)
                print('Done!')
            else:
                raise MethodInputException('Too much input parameters')


if __name__ == "__main__":
    script()
