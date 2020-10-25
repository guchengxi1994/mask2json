<!--
 * @lanhuage: markdown
 * @Descripttion: 
 * @version: beta
 * @Author: xiaoshuyui
 * @Date: 2020-10-22 09:36:45
 * @LastEditors: xiaoshuyui
 * @LastEditTime: 2020-10-23 09:42:44
-->
# This function is used to augment images, labels,masks, jsons and xmls.

## How to use.

### 1.For labelme(images and jsons).

    from convertmask.utils.imgAug import imgFlip, imgNoise, imgRotation, imgTranslation, aug_labelme, aug_labelimg, imgZoom
    import os
    from skimage import io
    from convertmask.utils.getMultiShapes import getMultiShapes

    BASE_DIR = os.path.abspath(os.path.dirname(os.getcwd())) + os.sep + 'static'
    imgPath = BASE_DIR + os.sep + 'multi_objs.jpg'
    labelPath = BASE_DIR + os.sep + 'multi_objs.json'

    if __name__ == "__main__":

        #### test1

        imgFlip(imgPath, labelPath)

        imgNoise(imgPath, labelPath)

        imgRotation(imgPath, labelPath)

        imgTranslation(imgPath, labelPath)

        imgZoom(imgPath, labelPath, 1.2)

        #### test2

        n = imgNoise(imgPath, labelPath, flag=False)

        tmp = n['noise']

        img, processedImg = tmp.oriImg, tmp.processedImg

        r = imgRotation(img, processedImg, flag=False, angle=15)

        tmp = r['rotation']

        img, processedImg = tmp.oriImg, tmp.processedImg

        t = imgTranslation(img, processedImg, flag=False)

        tmp = t['trans']

        img, processedImg = tmp.oriImg, tmp.processedImg

        f = imgFlip(img, processedImg, flag=False)

        tmp = f['h_v']

        img, processedImg = tmp.oriImg, tmp.processedImg

        parent_path = os.path.dirname(imgPath)

        if os.path.exists(parent_path + os.sep + 'jsons_'):
            pass
        else:
            os.makedirs(parent_path + os.sep + 'jsons_')
        fileName = 'test'
        io.imsave(
            parent_path + os.sep + 'jsons_' + os.sep + fileName + '_assumble.jpg',
            img)

        assumbleJson = getMultiShapes(parent_path + os.sep + 'jsons_' + os.sep +
                                    fileName + '_assumble.jpg',
                                    processedImg,
                                    flag=True,
                                    labelYamlPath='')

        saveJsonPath = parent_path + os.sep + 'jsons_' + os.sep + fileName + '_assumble.json'

        with open(saveJsonPath, 'w') as f:
            f.write(assumbleJson)

        #### test3

        aug_labelme(imgPath, labelPath)

### 2.For labelImg(images and xmls).

Just same as 'For labelme(images and jsons)'. For more detailed information,see [here](../../convertmask/utils/imgAug_xmls.py)