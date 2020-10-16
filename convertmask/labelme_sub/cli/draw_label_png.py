'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-10-16 10:08:47
LastEditors: xiaoshuyui
LastEditTime: 2020-10-16 11:01:04
'''
import argparse

import matplotlib.pyplot as plt
import numpy as np
import PIL.Image

from convertmask.labelme_sub.logger import logger
from convertmask.labelme_sub import utils


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('label_png', help='label PNG file')
    args = parser.parse_args()

    lbl = np.asarray(PIL.Image.open(args.label_png))

    logger.info('label shape: {}'.format(lbl.shape))
    logger.info('unique label values: {}'.format(np.unique(lbl)))

    lbl_viz = utils.draw_label(lbl)
    plt.imshow(lbl_viz)
    plt.show()


if __name__ == '__main__':
    main()
