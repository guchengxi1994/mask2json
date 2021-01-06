'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2021-01-04 11:25:08
LastEditors: xiaoshuyui
LastEditTime: 2021-01-05 10:16:06
'''
import sys
sys.path.append("..")

from convertmask import baseDecorate

@baseDecorate()
def test():
    print('this is a test script')

# @deprecated(message='')
# def test2():
#     print('this is a test script')

if __name__ == "__main__":
    test()

    # test2()