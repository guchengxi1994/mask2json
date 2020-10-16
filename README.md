<!--
 * @lanhuage: markdown
 * @Descripttion: 
 * @version: 
 * @Author: xiaoshuyui
 * @Date: 2020-06-09 16:23:03
 * @LastEditors: xiaoshuyui
 * @LastEditTime: 2020-10-16 10:15:07
--> 
[![Build Status](https://travis-ci.org/guchengxi1994/mask2json.svg?branch=master)](https://travis-ci.org/guchengxi1994/mask2json.svg?branch=test)

# mask2json

 a small tool for image augmentation, including mask files to json/xml files , image augmentation(flip,rotation,noise,...) and so on

 ## HOW TO USE

 This script is used to convert mask-labels to json files for [labelme](https://github.com/wkentaro/labelme).

 FIRST:

    pip install -r requestments.txt [-i https://pypi.tuna.tsinghua.edu.cn/simple/] 

 IF ERROR, try:

    pip install -r requirements.txt [-i https://pypi.tuna.tsinghua.edu.cn/simple/] --ignore-installed


AND THEN:

 Json files to masks can be found on this [site](https://blog.csdn.net/gaoyi135/article/details/103870646). Sometimes there will be an ERROR,should add this [file](./convertmask/labelme_sub/utils/draw.py) in labelme path (mine is '../anaconda/Lib/site-packages/labelme/utils ') and add some codes in \_\_init__.py:

    from .draw import label_colormap
    from .draw import _validate_colormap
    from .draw import label2rgb
    from .draw import draw_label
    from .draw import draw_instances 

### 'labelme_sub' folder is a copy of labelme (version 4.2.9) and i made some change.

Here shows an example using this script.

origin image

![img1](./static/1-2cvt.jpg)

mask image

![img1](./static/1-2cvt.png)

manually_labeled image

![img1](./backup/manually_labeled.png)

auto_labeled image

![img1](./backup/auto_labeled.png)
![img1](./backup/auto_labeled_ori.png)

Also ,for [labelimg](https://github.com/tzutalin/labelImg),a small tool to convert results(yolo) to [xml-files](./convertmask/utils/img2xml).

### (1) for labelme mask files

the test script can be found [here](./test_scripts/test_mask2json.py)

    from convertmask.utils import getMultiShapes
    getMultiShapes.getMultiShapes(param1,param2,param3,param4)

param1:path which saves the origin imgs

param2:path which saves the mask imgs (file names should match the origin imgs)

param3:converted json files save path

param4:can be blank (better don't), a yaml file path which saves the class information

### (2) for labelimg mask files

the test script can be found [here](./test_scripts/test_multiObjs2Xml.py)

    from convertmask.utils.getMultiShapes import getMultiObjs_voc as gvoc
    gvoc(param1,param2,param3)

param1:path which saves the origin imgs

param2:path which saves the mask imgs (file names should match the origin imgs)

param3:converted xml files save path

### (3) for json files  to mask files

the test script can be found [here](./test_scripts/json2mask.py)

    from convertmask.utils.convert import processor
    processor(param1,param2)

param1:json file or folder

param2:can be blank,encoding type, default 'utf-8'

### (4) for json files to xml files

the test script can be found [here](./test_scripts/test_json2xml.py)

    from convertmask.utils.json2xml import j2xConvert
    j2xConvert(path-of-your-jsonfile)

### (5) image augmentation

the test script can be found [here](./test_scripts/test_imgAug.py)

    from convertmask.utils.imgAug import imgFlip,imgNoise,imgRotation,imgTranslation,aug_labelme
    
    imgFlip(imgPath, labelPath)
    imgNoise(imgPath,labelPath)
    imgRotation(imgPath,labelPath)
    imgTranslation(imgPath,labelPath)

details see [Here](#2020.8.17)

## AILERNATIVE

you can try:

    pip install -U convertmask

and 

    pip uninstall convertmask

to delete convertmask.

it is a test release. : )

### version 0.3.1 (2020.8.20 , pre-release)

#### 1.try :

    convertmask -h | --help

to read the guide.

#### 2.try:

    convertmask -v | --version

to show the current version

#### 3.try:

    convertmask m2j 

to test mask to json function(should type in some file path)

#### 4.try:

    convertmask m2x 

to test mask to xml function(should type in some file path)

#### 5.try:

    convertmask j2m 

to test json to mask function(should type in some file path)

#### 6.try:

    convertmask j2x 

to test json to xml function(should type in some file path)

#### 7.try:

    convertmask aug 

to test image augmentation function(should type in some file path)




# CHANGE LOGS

## 2020.10.13

### 1.image augumentation support convert yolo txts to xmls(pascal). See [here](./test_scripts/test_yolo2xml.py)

### 2.speed up by using multiprocess

## 2020.10.12

### 1.image augumentation support generating several annotation/images with single image/annotation(json,xml). See [here](./test_scripts/test_multiAug.py)


## 2020.9.24

### 1.inspired by [LabelImgTool](https://github.com/lzx1413/LabelImgTool), convert xmls to jsons is useful. Also ,i forked this repo and add some pyqt5/py3 support,see [here](https://github.com/guchengxi1994/LabelImgTool).

examples:

script [here](./test_scripts/test_xml2json.py)

![gif1](./backup/xml2json.gif)



## 2020.8.24

### support convert xml files to yolo files. see [here](./test_scripts/test_xml2yolo.py)

examples:


![gif1](./backup/xml2yolo.gif)


## 2020.8.19

### 1. image translation supported.

![img1](./backup/translation.png)

combination of every augmentation method.

![img1](./backup/combine.png)

### 2. besides, a simple way convert json file(labelme) to xml file(labelImg) is provided. see [here](./test_scripts/test_json2xml.py)

![img1](./backup/json2xml.png)


## 2020.8.17

### 1. bug fix.

### 2. support image augmentation methods: noise,flip,rotation. try [test_imgAug.py](./test_scripts/test_imgAug.py) !

here are some examples:

### flip

![img1](./backup/flip_h.png)

![img1](./backup/flip_v.png)

![img1](./backup/flip_v_h.png)

### noise

![img1](./backup/noise.png)

### rotation

![img1](./backup/rotation.png)


## 2020.8.14

### 1. add image augmentation  (image flip) test. see [test_imgAug.py](./test_scripts/test_imgAug.py) !


## 2020.7.14

### 1.bugfix , test multi objects to xml files, pretty xmls

eg:

![img1](./backup/auto_mask2xml.png)


## 2020.7.13

### 1. convert multi objects to xml files supported (untested)


## 2020.7.10

### 1. a lot of things to do ,such as many warnings related to labelme.


## 2020.6.12

### 1.support multiple objects mask to json

try [test.py](./test_scripts/test.py) !

#### 1.1 multiple objects in different classes

manually_labeled image

![img1](./backup/manually_labeled_multi_objs.png)

auto_labeled image

![img1](./backup/auto_labeled_multi_objs.png)

#### 1.2 multiple objects in same classes

manually_labeled image

![img1](./backup/manually_labeled_multi_objs_samelabel.png)

auto_labeled image

![img1](./backup/auto_labeled_labeled_multi_objs_samelabel.png)



# what to do next

## 1. ~~support multiple files image augmentation~~ (2020.8.21)

## 2. ~~support image augmentation without a label/json file~~  (2020.8.21)

## 3. ~~support image augmentation with a labeled file (just support json file right now)~~ (2020.9)

## 4. image augmentation supports custom parameters (auto augmented right now)

## 5. do something more interesting

## 6. re-write main [script](./convertmask/m2j_m.py)

## 7. solve PyYmal installation error(currently write a [script](./convertmask/utils/methods/yamlUtils.py) by myself. maybe failure in the end.)

## 8. ~~image augmentation zoooom~~ (2020.10.14) 



# OTHERS

1. [issue:json2mask has no output](https://github.com/guchengxi1994/mask2json/issues/3)


![gif2](./backup/json2mask.gif)

if you test the [json2mask.py](./test_scripts/json2mask.py) script, you should change the path first and make sure the file is valid(maybe i have deleted :) )

Also, this script is just a reverse of mask2json, for a more COOOOOL method, see [here](./convertmask/utils/convert.py) , try convert.processor




#  SHORTCOMING

1.~~objects connected to each other is not supported yet.~~

this may happen if you labelling multiple-object-images with only 2 labels .Or some objects are of the same type and are connected to each other(eg. a bunch of grapes,it is hard to split one to the other).


2.Image Binarization [issue](https://github.com/guchengxi1994/mask2json/issues/14)
