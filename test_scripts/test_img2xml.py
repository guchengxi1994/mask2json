'''
@lanhuage: python
@Descripttion:  img2xml test script
@version: beta
@Author: xiaoshuyui
@Date: 2020-07-10 09:11:39
LastEditors: xiaoshuyui
LastEditTime: 2020-10-10 15:44:40
'''
import sys

sys.path.append("..")
from convertmask.utils.img2xml import processor_single_object

if __name__ == "__main__":
    """
    will cause some error on Windows \n
    such as the file or dirname starts with 't' or 'n' or numbers \n
    """

    f = open("./test_img2xml", 'w')
    f.writelines(
        processor_single_object.img2xml("test", "aa", "test\\test.xx", 12, 23,
                                    "aaa", 123, 444, 4523, 664))
    f.close()
