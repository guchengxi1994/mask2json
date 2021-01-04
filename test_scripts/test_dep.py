'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2021-01-04 11:25:08
LastEditors: xiaoshuyui
LastEditTime: 2021-01-04 13:46:52
'''
import sys
sys.path.append("..")

from convertmask import deprecated

@deprecated()
def test():
    print('this is a test script')

# @deprecated(message='')
# def test2():
#     print('this is a test script')

if __name__ == "__main__":
    test()

    # test2()