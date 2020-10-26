import sys

sys.path.append("..")
import os

from skimage import io
from convertmask.utils.auglib.optional.resize import resize_img,resizeScript

if __name__ == "__main__":
    BASE_DIR = os.path.abspath(os.path.dirname(
        os.getcwd())) + os.sep + 'static'
    imgPath = BASE_DIR + os.sep + 'testResize.jpg'
    xmlPath = BASE_DIR + os.sep + 'multi_objs.xml'
    oriImg = io.imread(BASE_DIR + os.sep + 'multi_objs.jpg')
    # resizeImg = resize_img(oriImg,heightFactor=0.5,widthFactor=1)

    # io.imsave(imgPath,resizeImg)

    img,path = resizeScript(oriImg,xmlPath,heightFactor=0.5,widthFactor=1)

    imgPath = path.replace('.xml','.jpg')
    io.imsave(imgPath,img)
