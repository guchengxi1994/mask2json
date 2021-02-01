'''
lanhuage: python
Descripttion:  copy from labelme/logger.py
version: beta
Author: xiaoshuyui
Date: 2020-08-19 08:59:04
LastEditors: xiaoshuyui
LastEditTime: 2021-01-13 13:55:26
'''
import logging

import termcolor
from convertmask import __appname__,__current_platform__

COLORS = {
    'WARNING': 'yellow',
    'INFO': 'white',
    'DEBUG': 'blue',
    'CRITICAL': 'red',
    'ERROR': 'red',
}


class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color=True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            if __current_platform__ != 'Windows':
                colored_levelname = termcolor.colored('[{}]'.format(levelname),
                                                      color=COLORS[levelname])
            else:
                colored_levelname = levelname
            record.levelname = colored_levelname
        return logging.Formatter.format(self, record)


class ColoredLogger(logging.Logger):
    if __current_platform__ != "Windows":
        fmt_filename = termcolor.colored('%(filename)s', attrs={'bold': True})
    else:
        fmt_filename = '%(filename)s'
    FORMAT = '%(levelname)s %(message)s ({}:%(lineno)d)'.format(fmt_filename)

    def __init__(self, name):
        logging.Logger.__init__(self, name, logging.INFO)

        color_formatter = ColoredFormatter(self.FORMAT)

        console = logging.StreamHandler()
        console.setFormatter(color_formatter)

        self.addHandler(console)
        return


logging.setLoggerClass(ColoredLogger)
logger = logging.getLogger(__appname__)