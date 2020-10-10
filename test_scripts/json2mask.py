'''
@lanhuage: python
@Descripttion: 
@version: beta
@Author: xiaoshuyui
@Date: 2020-06-12 09:32:14
LastEditors: xiaoshuyui
LastEditTime: 2020-10-10 15:36:32
'''
# coding: utf-8
import argparse
import json
import os
import os.path as osp
import warnings
import numpy as np
import PIL.Image
import yaml
from labelme import utils


def main():
    json_file = 'D:\\testALg\\mask2json\\mask2json\\static\\'  #json path
    list = os.listdir(json_file)
    for i in range(0, len(list)):
        path = os.path.join(json_file, list[i])
        if os.path.isfile(path) and path.endswith('.json'):
            data = json.load(open(path))
            img = utils.img_b64_to_arr(data['imageData'])
            lbl, lbl_names = utils.labelme_shapes_to_label(
                img.shape, data['shapes'])
            # lbl[lbl>0] = 255
            # print(lbl)

            captions = [
                '%d: %s' % (l, name) for l, name in enumerate(lbl_names)
            ]
            lbl_viz = utils.draw_label(lbl, img, captions)
            out_dir = osp.basename(list[i]).replace('.', '_')
            out_dir = osp.join(osp.dirname(list[i]), out_dir)
            if not osp.exists(out_dir):
                os.mkdir(out_dir)
            PIL.Image.fromarray(img).save(osp.join(out_dir, 'img.png'))
            PIL.Image.fromarray(lbl).save(osp.join(out_dir, 'label.png'))
            print(np.max(lbl))
            lbl = np.array(lbl, dtype=np.uint8)
            lbl[lbl > 0] = 255

            PIL.Image.fromarray(lbl).save(osp.join(out_dir, 'label_255.png'))
            PIL.Image.fromarray(lbl_viz).save(
                osp.join(out_dir, 'label_viz.png'))
            with open(osp.join(out_dir, 'label_names.txt'), 'w') as f:
                for lbl_name in lbl_names:
                    f.write(lbl_name + '\n')
            warnings.warn('info.yaml is being replaced by label_names.txt')
            info = dict(label_names=lbl_names)
            with open(osp.join(out_dir, 'info.yaml'), 'w') as f:
                yaml.safe_dump(info, f, default_flow_style=False)
            print('Saved to: %s' % out_dir)


def singleFile(filePath):
    if os.path.isfile(filePath) and filePath.endswith('.json'):
        data = json.load(open(filePath))
        img = utils.img_b64_to_arr(data['imageData'])
        lbl, lbl_names = utils.labelme_shapes_to_label(img.shape,
                                                       data['shapes'])
        # lbl[lbl>0] = 255
        # print(lbl)

        captions = ['%d: %s' % (l, name) for l, name in enumerate(lbl_names)]
        lbl_viz = utils.draw_label(lbl, img, captions)
        out_dir = osp.basename(filePath).replace('.', '_')
        out_dir = osp.join(osp.dirname(filePath), out_dir)
        if not osp.exists(out_dir):
            os.mkdir(out_dir)
        PIL.Image.fromarray(img).save(osp.join(out_dir, 'img.png'))
        PIL.Image.fromarray(lbl).save(osp.join(out_dir, 'label.png'))
        print(np.max(lbl))
        lbl = np.array(lbl, dtype=np.uint8)
        lbl[lbl > 0] = 255

        PIL.Image.fromarray(lbl).save(osp.join(out_dir, 'label_255.png'))
        PIL.Image.fromarray(lbl_viz).save(osp.join(out_dir, 'label_viz.png'))
        with open(osp.join(out_dir, 'label_names.txt'), 'w') as f:
            for lbl_name in lbl_names:
                f.write(lbl_name + '\n')
        warnings.warn('info.yaml is being replaced by label_names.txt')
        info = dict(label_names=lbl_names)
        with open(osp.join(out_dir, 'info.yaml'), 'w') as f:
            yaml.safe_dump(info, f, default_flow_style=False)
        print('Saved to: %s' % out_dir)


if __name__ == '__main__':
    # main()
    singleFile(
        'D:\\testALg\\mask2json\\mask2json\\static\\multi_objs_sameclass.json')
