'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2021-01-13 15:38:13
LastEditors: xiaoshuyui
LastEditTime: 2021-01-14 15:20:36
'''
import sys
sys.path.append('..')

from convertmask.utils.train_val_dataset_split.yololike import split

if __name__ == "__main__":
    split('D:\\mask2json\\test\\',
          'D:\\mask2json\\test_scripts\\DevLog')
