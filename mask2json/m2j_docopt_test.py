'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-08-14 15:55:55
LastEditors: xiaoshuyui
LastEditTime: 2020-08-14 16:04:11

convertmask

Usage:
    m2j_docopt_test.py  (-h | --help)

options:
    -h --help   Show this screen.
   

'''

from docopt import docopt
import os
import sys
sys.path.append('..')

if __name__ == "__main__":
    arguments = docopt(__doc__)
    print(arguments)