<!--
 * @lanhuage: markdown
 * @Descripttion: 
 * @version: beta
 * @Author: xiaoshuyui
 * @Date: 2020-11-09 14:09:12
 * @LastEditors: xiaoshuyui
 * @LastEditTime: 2020-11-09 14:12:15
-->
# This function is used to convert masks to jsons.

## How to use.

```python

    from convertmask.utils.methods import getMultiShapes

    imgPath = 'D:\\testALg\\mask2json\\mask2json\\static\\multi_objs_test.jpg'
    maskPath = 'D:\\testALg\\mask2json\\mask2json\\static\\multi_objs_json\\label.png'
    savePath = 'D:\\testALg\\mask2json\\mask2json\\static\\multi_objs_json\\1109\\'
    yamlPath = 'D:\\testALg\\mask2json\\mask2json\\static\\multi_objs_json\\info.yaml'
    getMultiShapes.getMultiShapes(imgPath, maskPath, savePath, yamlPath)  # with yaml

    getMultiShapes.getMultiShapes(imgPath, maskPath, savePath)  # without yaml
```