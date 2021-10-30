'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-07-01 11:06:44
LastEditors: xiaoshuyui
LastEditTime: 2021-02-19 16:49:37
'''

import json
import os
import os.path as osp

import convertmask
import PIL.Image
import yaml
from convertmask.utils.methods.logger import logger

isInstalled = True

try:
    from labelme.utils import draw_label
except:
    isInstalled = False

import labelme.utils as lUtils
import numpy as np
from tqdm import tqdm


def processor(json_file, encoding="utf-8", flag=False):
    """
    input a json folder,or single file path
    """
    if not os.path.exists(json_file):
        raise FileExistsError('Not Found')
    else:
        if os.path.isfile(json_file):
            if not json_file.endswith('.json'):
                raise TypeError('Must be a *.json file')
            else:
                parent_path = os.path.dirname(json_file) + os.sep
                try:
                    data = json.load(open(json_file, encoding=encoding))
                    img = lUtils.img_b64_to_arr(data['imageData'])

                    lbl, lbl_names = lUtils.labelme_shapes_to_label(
                        img.shape, data['shapes'])

                    captions = [
                        '%d: %s' % (l, name)
                        for l, name in enumerate(lbl_names)
                    ]

                    if isInstalled:
                        lbl_viz = lUtils.draw_label(lbl, img, captions)
                    else:
                        from convertmask.utils.draw import draw_label
                        lbl_viz =  draw_label(lbl, img, captions)

                    ##
                    if np.max(lbl) == 255 or np.max(lbl) == 1:
                        lbl[lbl > 0] = 255
                    ##

                    lbl = np.array(lbl, dtype=np.uint8)

                    if not flag:

                        out_dir = osp.basename(json_file).split('.json')[0]
                        save_file_name = out_dir

                        if not osp.exists(parent_path + 'mask'):
                            os.mkdir(parent_path + 'mask')
                        maskdir = parent_path + 'mask'

                        if not osp.exists(parent_path + 'mask_viz'):
                            os.mkdir(parent_path + 'mask_viz')
                        maskvizdir = parent_path + 'mask_viz'

                        out_dir1 = maskdir
                        PIL.Image.fromarray(lbl).save(out_dir1 + '/' +
                                                      save_file_name + '.png')
                        PIL.Image.fromarray(lbl_viz).save(maskvizdir + '/' +
                                                          save_file_name +
                                                          '_label_viz.png')
                        with open(osp.join(out_dir1, 'label_names.txt'),
                                  'w') as f:
                            for lbl_name in lbl_names:
                                f.write(lbl_name + '\n')

                        info = dict(label_names=lbl_names)
                        with open(osp.join(out_dir1, 'info.yaml'), 'w') as f:
                            yaml.safe_dump(info, f, default_flow_style=False)

                        print('Saved to: %s' % out_dir1)

                    else:
                        return lbl
                except Exception as e:
                    # print(e)
                    logger.error(e)

        else:
            list_path = os.listdir(json_file)
            # print('freedom =', json_file)
            for i in tqdm(range(0, len(list_path))):
                path = os.path.join(json_file, list_path[i])
                if os.path.isfile(path) and path.endswith('.json'):
                    try:
                        data = json.load(open(path, encoding=encoding))
                        img = lUtils.img_b64_to_arr(data['imageData'])
                        lbl, lbl_names = lUtils.labelme_shapes_to_label(
                            img.shape, data['shapes'])

                        captions = [
                            '%d: %s' % (l, name)
                            for l, name in enumerate(lbl_names)
                        ]

                        if isInstalled:
                            lbl_viz = lUtils.draw_label(lbl, img, captions)
                        else:
                            from convertmask.utils.draw import draw_label
                            lbl_viz =  draw_label(lbl, img, captions)

                        # lbl[lbl>0] = 255
                        if np.max(lbl) == 255 or np.max(lbl) == 1:
                            lbl[lbl > 0] = 255
                        lbl = np.array(lbl, dtype=np.uint8)

                        # out_dir = osp.basename(path).replace('.', '_')
                        out_dir = osp.basename(path).split('.json')[0]
                        save_file_name = out_dir
                        # out_dir = osp.join(osp.dirname(path), out_dir)

                        if not osp.exists(json_file + 'mask'):
                            os.mkdir(json_file + 'mask')
                        maskdir = json_file + 'mask'

                        if not osp.exists(json_file + 'mask_viz'):
                            os.mkdir(json_file + 'mask_viz')
                        maskvizdir = json_file + 'mask_viz'

                        out_dir1 = maskdir
                        # if not osp.exists(out_dir1):
                        #     os.mkdir(out_dir1)

                        # PIL.Image.fromarray(img).save(out_dir1 + '\\' + save_file_name + '_img.png')
                        PIL.Image.fromarray(lbl).save(out_dir1 + '/' +
                                                      save_file_name + '.png')

                        PIL.Image.fromarray(lbl_viz).save(maskvizdir + '/' +
                                                          save_file_name +
                                                          '_label_viz.png')

                        with open(osp.join(out_dir1, 'label_names.txt'),
                                  'w') as f:
                            for lbl_name in lbl_names:
                                f.write(lbl_name + '\n')

                        # warnings.warn('info.yaml is being replaced by label_names.txt')
                        info = dict(label_names=lbl_names)
                        with open(osp.join(out_dir1, 'info.yaml'), 'w') as f:
                            yaml.safe_dump(info, f, default_flow_style=False)

                        print('Saved to: %s' % out_dir1)
                    except Exception as e:
                        # print(e)
                        logger.error(e)


# if __name__ == '__main__':
#     # base64path = argv[1]
#     main()
