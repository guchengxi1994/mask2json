'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-10-20 16:50:35
LastEditors: xiaoshuyui
LastEditTime: 2020-10-20 19:02:47
'''

from convertmask.utils.methods.logger import logger
import json
import os
import yaml
import cv2
import io
import traceback
import PIL

isInstalled = True

try:
    from labelme.utils import draw_label
except:
    isInstalled = False
if isInstalled:
    import labelme.utils as lUtils  # solve conflict
else:
    from convertmask.labelme_sub import utils as lUtils

import numpy as np
from tqdm import tqdm


def processor(json_file, yaml_file, encoding='utf-8', flag=False):
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
                    mask = generateMaskFile(data, yaml_file)

                    lbl_names = getYamlKeys(yaml_file)

                    captions = [
                        '%d: %s' % (l, name)
                        for l, name in enumerate(lbl_names)
                    ]

                    lbl_viz = draw_label(mask, img, captions)

                    if not flag:
                        out_dir = os.path.basename(json_file).split('.json')[0]
                        save_file_name = out_dir

                        if not os.path.exists(parent_path + 'masks_'):
                            os.mkdir(parent_path + 'masks_')

                        if not os.path.exists(parent_path + 'masks_' + os.sep +
                                              'mask'):
                            os.mkdir(parent_path + 'masks_' + os.sep + 'mask')
                        maskdir = parent_path + 'masks_' + os.sep + 'mask'

                        if not os.path.exists(parent_path + 'masks_' + os.sep +
                                              'mask_viz'):
                            os.mkdir(parent_path + 'masks_' + os.sep +
                                     'mask_viz')
                        maskvizdir = parent_path + 'masks_' + os.sep + 'mask_viz'

                        out_dir1 = maskdir
                        PIL.Image.fromarray(mask).save(out_dir1 + '/' +
                                                       save_file_name + '.png')
                        PIL.Image.fromarray(lbl_viz).save(maskvizdir + '/' +
                                                          save_file_name +
                                                          '_label_viz.png')

                        with open(os.path.join(out_dir1, 'label_names.txt'),
                                  'w') as f:
                            for lbl_name in lbl_names:
                                f.write(lbl_name + '\n')

                        info = dict(label_names=lbl_names)
                        with open(os.path.join(out_dir1, 'info.yaml'),
                                  'w') as f:
                            yaml.safe_dump(info, f, default_flow_style=False)

                        print(parent_path + 'masks_')
                    else:
                        return mask

                except:
                    traceback.print_exc()

        else:
            list_path = os.listdir(json_file)
            for i in tqdm(range(0, len(list_path))):
                path = os.path.join(json_file, list_path[i])
                if os.path.isfile(path) and path.endswith('.json'):
                    try:
                        data = json.load(open(path, encoding=encoding))
                        img = lUtils.img_b64_to_arr(data['imageData'])

                        lbl = generateMaskFile(data, yaml_file)

                        lbl_names = getYamlKeys(yaml_file)

                        captions = [
                            '%d: %s' % (l, name)
                            for l, name in enumerate(lbl_names)
                        ]

                        lbl_viz = draw_label(lbl, img, captions)

                        # lbl[lbl>0] = 255
                        if np.max(lbl) == 255 or np.max(lbl) == 1:
                            lbl[lbl > 0] = 255
                        lbl = np.array(lbl, dtype=np.uint8)

                        out_dir = os.path.basename(path).split(
                            '.json')[0] + os.sep
                        save_file_name = out_dir

                        if not os.path.exists(json_file + 'mask'):
                            os.mkdir(json_file + 'mask')
                        maskdir = json_file + 'mask'

                        if not os.path.exists(json_file + 'mask_viz'):
                            os.mkdir(json_file + 'mask_viz')
                        maskvizdir = json_file + 'mask_viz'

                        out_dir1 = maskdir
                        
                        PIL.Image.fromarray(lbl).save(out_dir1 + '/' +
                                                      save_file_name + '.png')
                        PIL.Image.fromarray(lbl_viz).save(maskvizdir + '/' +
                                                          save_file_name +
                                                          '_label_viz.png')

                        with open(os.path.join(out_dir1, 'label_names.txt'),
                                  'w') as f:
                            for lbl_name in lbl_names:
                                f.write(lbl_name + '\n')

                        # warnings.warn('info.yaml is being replaced by label_names.txt')
                        info = dict(label_names=lbl_names)
                        with open(os.path.join(out_dir1, 'info.yaml'),
                                  'w') as f:
                            yaml.safe_dump(info, f, default_flow_style=False)

                        print('Saved to: %s' % out_dir1)
                    except Exception as e:
                        # print(e)
                        logger.error(e)


def generateMaskFile(data, yamlFile):
    imageHeight = data["imageHeight"]
    imageWidth = data["imageWidth"]
    mask = np.zeros((imageHeight, imageWidth)).astype(np.uint8)
    try:
        shapes = data['shapes']
        for i in shapes:
            k = i["label"]
            v = readYamlFileVals(yamlFile, k)
            polygon = i["points"]
            if v != 0:
                mask = draw_mask(polygon, mask, int(v))
        # print(np.max(mask))
        return mask

    except Exception as e:
        logger.error(e)

    # print(shapes)


def draw_mask(polygon: list, mask: np.ndarray, val: int):
    area = np.array([polygon])
    # mask = cv2.merge([mask,mask,mask])
    cv2.fillPoly(mask, area, val)
    return mask


def readYamlFileVals(yamlFile, k):
    f = open(yamlFile, 'r', encoding='utf-8')
    x = yaml.load(f.read(), Loader=yaml.FullLoader)
    try:
        res = x['label_names'][k]
        return res
    except:
        return 0
    finally:
        f.close()


def getYamlKeys(yamlFile):
    f = open(yamlFile, 'r', encoding='utf-8')
    x = yaml.load(f.read(), Loader=yaml.FullLoader)
    # print(x['label_names'])
    return x['label_names']


def draw_label(label, img=None, label_names=None, colormap=None, **kwargs):
    """Draw pixel-wise label with colorization and label names.

    label: ndarray, (H, W)
        Pixel-wise labels to colorize.
    img: ndarray, (H, W, 3), optional
        Image on which the colorized label will be drawn.
    label_names: iterable
        List of label names.
    """
    import matplotlib.pyplot as plt

    backend_org = plt.rcParams['backend']
    plt.switch_backend('agg')

    plt.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0, hspace=0)
    plt.margins(0, 0)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())

    if label_names is None:
        label_names = [str(l) for l in range(label.max() + 1)]

    colormap = _validate_colormap(colormap, len(label_names))

    label_viz = label2rgb(label,
                          img,
                          n_labels=len(label_names),
                          colormap=colormap,
                          **kwargs)
    plt.imshow(label_viz)
    plt.axis('off')

    plt_handlers = []
    plt_titles = []
    for label_value, label_name in enumerate(label_names):
        if label_value not in label:
            continue
        fc = colormap[label_value]
        p = plt.Rectangle((0, 0), 1, 1, fc=fc)
        plt_handlers.append(p)
        plt_titles.append('{value}: {name}'.format(value=label_value,
                                                   name=label_name))
    plt.legend(plt_handlers, plt_titles, loc='lower right', framealpha=.5)

    f = io.BytesIO()
    plt.savefig(f, bbox_inches='tight', pad_inches=0)
    plt.cla()
    plt.close()

    plt.switch_backend(backend_org)

    out_size = (label_viz.shape[1], label_viz.shape[0])
    out = PIL.Image.open(f).resize(out_size, PIL.Image.BILINEAR).convert('RGB')
    out = np.asarray(out)
    return out


def _validate_colormap(colormap, n_labels):
    if colormap is None:
        colormap = lUtils.label_colormap(n_labels)
    else:
        assert colormap.shape == (colormap.shape[0], 3), \
            'colormap must be sequence of RGB values'
        assert 0 <= colormap.min() and colormap.max() <= 1, \
            'colormap must ranges 0 to 1'
    return colormap


# similar function as skimage.color.label2rgb
def label2rgb(
    lbl,
    img=None,
    n_labels=None,
    alpha=0.5,
    thresh_suppress=0,
    colormap=None,
):
    if n_labels is None:
        n_labels = len(np.unique(lbl))

    # print(lbl)
    lbl = reLabeled(n_labels, lbl)
    colormap = _validate_colormap(colormap, n_labels)
    colormap = (colormap * 255).astype(np.uint8)

    lbl_viz = colormap[lbl]
    lbl_viz[lbl == -1] = (0, 0, 0)  # unlabeled

    if img is not None:
        img_gray = PIL.Image.fromarray(img).convert('LA')
        img_gray = np.asarray(img_gray.convert('RGB'))
        # img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        # img_gray = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2RGB)
        lbl_viz = alpha * lbl_viz + (1 - alpha) * img_gray
        lbl_viz = lbl_viz.astype(np.uint8)

    return lbl_viz


def reLabeled(n_labels, lbl: np.ndarray):
    tmp = np.unique(lbl)
    tmp.sort()
    # print(tmp)
    for i in range(0, n_labels):
        # pass
        if tmp[i] == 0:
            pass
        else:
            lbl[lbl == tmp[i]] = i
    return lbl
