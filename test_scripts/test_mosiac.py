import sys

sys.path.append("..")
import os

from skimage import io
from convertmask.utils.auglib.optional.mosaic import mosiac_img,mosiacScript

BASE_DIR = os.path.abspath(os.path.dirname(
        os.getcwd())) + os.sep + 'static'

if __name__ == "__main__":
    BASE_DIR = os.path.abspath(os.path.dirname(
        os.getcwd())) + os.sep + 'static'
    imgPath = BASE_DIR + os.sep + 'testMosiac.jpg'
    xmlPath = BASE_DIR + os.sep + 'multi_objs.xml'
    oriImg = io.imread(BASE_DIR + os.sep + 'multi_objs.jpg')

    # mosicImg = mosiac_img([oriImg,],heightFactor=0.7,widthFactor=0.3)
    # io.imsave(imgPath,mosicImg)

    mosiacScript([oriImg,],[xmlPath,],BASE_DIR,True)