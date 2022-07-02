<!--
 * @lanhuage: markdown
 * @Descripttion: 
 * @version: beta
 * @Author: xiaoshuyui
 * @Date: 2020-10-22 09:30:05
 * @LastEditors: xiaoshuyui
 * @LastEditTime: 2020-10-23 09:15:36
-->
# This function is used to split a long image to small images in specific conditions.

## How to use.

```python

    import os
    import glob
    from convertmask.utils.longImgSplit import script as sc
    
    save_dir = os.path.abspath(os.path.dirname(
        os.getcwd())) + os.sep + 'static' + os.sep + "testXmlSplit" + os.sep

    if __name__ == "__main__":
        imgPath = 'file-of-your-images'
        xmlPath = 'file-of-your-xmls'

        xmls = glob.glob(xmlPath + os.sep + '*.xml')
        imgs = glob.glob(imgPath + os.sep + '*.jpg')

        for i in xmls:
            imgName = i.split(os.sep)[-1][:-4]
            img = imgPath + os.sep + imgName + ".jpg"
            sc.convertImgSplit(img, i, yamlPath=save_dir + 'info2.yaml', bias=2000)
```

# This function maybe some errors.