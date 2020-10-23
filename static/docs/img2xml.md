<!--
 * @lanhuage: markdown
 * @Descripttion: 
 * @version: beta
 * @Author: xiaoshuyui
 * @Date: 2020-10-22 09:29:10
 * @LastEditors: xiaoshuyui
 * @LastEditTime: 2020-10-23 08:41:34
-->
# This function is used to convert images information to xmls.

### For example, if you have a trained model, you can generate annotations of test images after getting class names and bounding boxes (just for labelImg, like [this](../multi_objs.xml)).

## How to use.

For testing, just try this [script](../../test_scripts/test_img2xml.py)

    from convertmask.utils.img2xml import processor_singleObj
    if __name__ == "__main__":
    
    """will cause some error on Windows \n
    such as the file or dirname starts with 't' or 'n' or numbers \n
    """

    f = open("./test_img2xml", 'w')
    f.writelines(
        processor_singleObj.img2xml("test", "aa", "test\\test.xx", 12, 23,
                                    "aaa", 123, 444, 4523, 664))
    f.close()

This is for single object. The function 'img2xml' needs a parameter list like:
(folder:str,filename:str,path:str,width:int,height:int,name:str, 
    xmin:int,ymin:int,xmax:int,ymax:int) 

For multiple objects, try processor_multiObj.py. The function 'img2xml_multiobj' needs a parameter list like:
(tmpPath: str, aimPath: str, folder: str, filename: str,
                     path: str, width: int, height: int, objs: list)

parameter 'tmpPath' can be same as parameter 'aimPath'.
parameter 'objs' is a list like '\[{'name':'xxx','difficult':0,'bndbox':{'xmin':??,...,'ymax':??}}\]'