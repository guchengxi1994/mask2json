<!--
 * @lanhuage: markdown
 * @Descripttion: 
 * @version: beta
 * @Author: xiaoshuyui
 * @Date: 2020-10-22 09:29:21
 * @LastEditors: xiaoshuyui
 * @LastEditTime: 2020-10-23 09:05:32
-->
# This function is used to convert jsons(labelme) to masks.

## How to use.

    from convertmask.utils.json2mask.convertWithLabel import processor

    BASE_DIR = os.path.abspath(os.path.dirname(os.getcwd())) + os.sep + 'static'
    imgPath = BASE_DIR + os.sep + 'multi_objs.jpg'
    labelPath = BASE_DIR + os.sep + 'multi_objs.json'
    yamlFilePath = BASE_DIR + os.sep + 'multi_objs.yaml'

    if __name__ == "__main__":
        processor(labelPath,yamlFilePath)

If you want to test the function on your own, should change the file path.

The parameter list is like:(json_file, yaml_file, encoding='utf-8', flag=False)

Parameter 'json_file' is a labelme generated file, yaml_file is the class file like [this](../multi_objs.yaml), and is necessary in this function. Without this file, there will be some errors when converting multiple objects to masks (especially for multi files).

Parameter 'flag' is determining whether you want to save files like [this](../mask_viz/multi_objs_sameclass_label_viz.png)

# Converting jsons to masks without yaml files is not recommended. If you do want to have a try, try this [function](../../convertmask/utils/json2mask/convert.py).