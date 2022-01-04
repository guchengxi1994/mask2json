'''
@lanhuage: python
@Descripttion: 图像增广
@version: beta
@Author: xiaoshuyui
@Date: 2020-03-11 10:09:17
LastEditors: xiaoshuyui
LastEditTime: 2020-10-10 15:45:30
'''
import cv2
import math
import numpy as np
import os
try:
    import defusedxml.ElementTree as ET
except:
    import xml.etree.ElementTree as ET


class ImgAugemention():
    def __init__(self):
        self.angle = 90

    # rotate_img
    def rotate_image(self, src, angle, scale=1.):
        w = src.shape[1]
        h = src.shape[0]
        # convet angle into rad
        rangle = np.deg2rad(angle)  # angle in radians
        # calculate new image width and height
        nw = (abs(np.sin(rangle) * h) + abs(np.cos(rangle) * w)) * scale
        nh = (abs(np.cos(rangle) * h) + abs(np.sin(rangle) * w)) * scale
        # ask OpenCV for the rotation matrix
        rot_mat = cv2.getRotationMatrix2D((nw * 0.5, nh * 0.5), angle, scale)
        # calculate the move from the old center to the new center combined
        # with the rotation
        rot_move = np.dot(rot_mat, np.array([(nw - w) * 0.5, (nh - h) * 0.5,
                                             0]))
        # the move only affects the translation, so update the translation
        # part of the transform
        rot_mat[0, 2] += rot_move[0]
        rot_mat[1, 2] += rot_move[1]
        # map
        return cv2.warpAffine(src,
                              rot_mat,
                              (int(math.ceil(nw)), int(math.ceil(nh))),
                              flags=cv2.INTER_LANCZOS4)

    def rotate_xml(self, src, xmin, ymin, xmax, ymax, angle, scale=1.):
        w = src.shape[1]
        h = src.shape[0]
        rangle = np.deg2rad(angle)  # angle in radians
        # now calculate new image width and height
        # get width and heigh of changed image
        nw = (abs(np.sin(rangle) * h) + abs(np.cos(rangle) * w)) * scale
        nh = (abs(np.cos(rangle) * h) + abs(np.sin(rangle) * w)) * scale
        # ask OpenCV for the rotation matrix
        rot_mat = cv2.getRotationMatrix2D((nw * 0.5, nh * 0.5), angle, scale)
        # calculate the move from the old center to the new center combined
        # with the rotation
        rot_move = np.dot(rot_mat, np.array([(nw - w) * 0.5, (nh - h) * 0.5,
                                             0]))
        # the move only affects the translation, so update the translation
        # part of the transform
        rot_mat[0, 2] += rot_move[0]
        rot_mat[1, 2] += rot_move[1]
        # rot_mat: the final rot matrix
        # get the four center of edges in the initial martix，and convert the coord
        point1 = np.dot(rot_mat, np.array([(xmin + xmax) / 2, ymin, 1]))
        point2 = np.dot(rot_mat, np.array([xmax, (ymin + ymax) / 2, 1]))
        point3 = np.dot(rot_mat, np.array([(xmin + xmax) / 2, ymax, 1]))
        point4 = np.dot(rot_mat, np.array([xmin, (ymin + ymax) / 2, 1]))
        # concat np.array
        concat = np.vstack((point1, point2, point3, point4))
        # change type
        concat = concat.astype(np.int32)
        print(concat)
        rx, ry, rw, rh = cv2.boundingRect(concat)
        return rx, ry, rw, rh

    """
    0:垂直翻转
    1：水平翻转
    -1：同时翻转
    """

    def flip_xml(self, src, xmin, ymin, xmax, ymax, flipType=0):
        # pass
        w = src.shape[1]
        h = src.shape[0]

        if flipType == 0:
            return xmin, h - ymax, xmax, h - ymin
        elif flipType == 1:
            return w - xmax, ymin, w - xmin, ymax
        else:
            return w - xmax, h - ymax, w - xmin, h - ymin

    def flip_img(self, src, flipType=0):
        # if flipType == 0:
        return cv2.flip(src, flipType)

    def _process_img_flip(self, imgs_path, xmls_path, img_save_path, xml_save_path, \
        flip_list=[1,0,-1]):

        for f in flip_list:
            for img_name in os.listdir(imgs_path):
                n, s = os.path.splitext(img_name)
                if s == ".jpg" and n + ".xml" in os.listdir(xmls_path):
                    img_path = os.path.join(imgs_path, img_name)
                    img = cv2.imread(img_path)
                    rotated_img = self.flip_img(img, f)
                    # 写入图像
                    cv2.imwrite(img_save_path + n + "_" + str(f) + "flip.jpg",
                                rotated_img)
                    # print("log: [%sd] %s is processed." % (f, img))
                    xml_url = img_name.split('.')[0] + '.xml'
                    xml_path = os.path.join(xmls_path, xml_url)
                    try:
                        tree = ET.parse(xml_path)
                        root = tree.getroot()

                        root.find('folder').text = str(img_save_path.split(os.sep)[-1] if \
                            img_save_path.split(os.sep)[-1] != "" else img_save_path.split(os.sep)[-2] )
                        root.find('filename').text = str(n + "_" + str(f) +
                                                         "flip.jpg")
                        root.find('path').text = str(img_save_path + n + "_" +
                                                     str(f) + "flip.jpg")

                        for box in root.iter('bndbox'):
                            xmin = float(box.find('xmin').text)
                            ymin = float(box.find('ymin').text)
                            xmax = float(box.find('xmax').text)
                            ymax = float(box.find('ymax').text)
                            xmin, ymin, xmax, ymax = self.flip_xml(
                                img, xmin, ymin, xmax, ymax, f)
                            # change the coord
                            box.find('xmin').text = str(int(xmin))
                            box.find('ymin').text = str(int(ymin))
                            box.find('xmax').text = str(int(xmax))
                            box.find('ymax').text = str(int(ymax))
                            box.set('updated', 'yes')
                        # write into new xml
                        tree.write(xml_save_path + n + "_" + str(f) +
                                   "flip.xml")
                        # print(xml_save_path + n + "_" + str(f) + "flip.xml")
                    except Exception as e:
                        # raise ValueError("no file")
                        print(e)
                        # pass
                    finally:
                        print("[%s] %s is processed." % (f, img_name))

    """
    直方图均衡化
    """

    def his(self, src):
        b, g, r = cv2.split(src)
        # 创建局部直方图均衡化
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(5, 5))
        # 对每一个通道进行局部直方图均衡化
        b = clahe.apply(b)
        g = clahe.apply(g)
        r = clahe.apply(r)
        # 合并处理后的三通道 成为处理后的图
        image = cv2.merge([b, g, r])

        return image

    def _process_img_his(self, imgs_path, xmls_path, img_save_path,
                         xml_save_path):

        for img_name in os.listdir(imgs_path):
            n, s = os.path.splitext(img_name)
            if s == ".jpg" and n + ".xml" in os.listdir(xmls_path):
                img_path = os.path.join(imgs_path, img_name)
                img = cv2.imread(img_path)
                # rotated_img = self.flip_img(img, f)
                his_img = self.his(img)
                # 写入图像
                cv2.imwrite(img_save_path + n + "_" + "HIS.jpg", his_img)
                # print("log: [%sd] %s is processed." % (f, img))
                xml_url = img_name.split('.')[0] + '.xml'
                xml_path = os.path.join(xmls_path, xml_url)
                try:
                    tree = ET.parse(xml_path)
                    root = tree.getroot()

                    root.find('folder').text = str(img_save_path.split(os.sep)[-1] if \
                        img_save_path.split(os.sep)[-1] != "" else img_save_path.split(os.sep)[-2] )
                    root.find('filename').text = str(n + "_" + "HIS.jpg")
                    root.find('path').text = str(img_save_path + n + "_" +
                                                 "HIS.jpg")

                    for box in root.iter('bndbox'):
                        xmin = float(box.find('xmin').text)
                        ymin = float(box.find('ymin').text)
                        xmax = float(box.find('xmax').text)
                        ymax = float(box.find('ymax').text)
                        # xmin,ymin,xmax,ymax = self.flip_xml(img, xmin, ymin, xmax, ymax, f)
                        # change the coord
                        box.find('xmin').text = str(int(xmin))
                        box.find('ymin').text = str(int(ymin))
                        box.find('xmax').text = str(int(xmax))
                        box.find('ymax').text = str(int(ymax))
                        box.set('updated', 'yes')
                    # write into new xml
                    tree.write(xml_save_path + n + "_" + "HIS.xml")
                    # print(xml_save_path + n + "_" + str(f) + "flip.xml")
                except Exception as e:
                    # raise ValueError("no file")
                    print(e)
                    # pass
                finally:
                    print("[%s] %s is processed." % ("HIS", img_name))

    def process_img(self, imgs_path, xmls_path, img_save_path, xml_save_path,
                    angle_list):
        # assign the rot angles
        for angle in angle_list:
            for img_name in os.listdir(imgs_path):
                # split filename and suffix
                n, s = os.path.splitext(img_name)
                print("================>" + n)
                # for the sake of use yol model, only process '.jpg'
                if s == ".jpg" and n + ".xml" in os.listdir(xmls_path):
                    img_path = os.path.join(imgs_path, img_name)
                    img = cv2.imread(img_path)
                    rotated_img = self.rotate_image(img, angle)
                    # 写入图像
                    cv2.imwrite(img_save_path + n + "_" + str(angle) + "d.jpg",
                                rotated_img)
                    # print("log: [%sd] %s is processed." % (angle, img))
                    xml_url = img_name.split('.')[0] + '.xml'
                    xml_path = os.path.join(xmls_path, xml_url)
                    try:
                        tree = ET.parse(xml_path)
                        root = tree.getroot()

                        root.find('folder').text = str(img_save_path.split(os.sep)[-1] if \
                                img_save_path.split(os.sep)[-1] != "" else img_save_path.split(os.sep)[-2] )
                        root.find('filename').text = str(n + "_" + str(angle) +
                                                         "d.jpg")
                        root.find('path').text = str(img_save_path + n + "_" +
                                                     str(angle) + "d.jpg")

                        for box in root.iter('bndbox'):
                            xmin = float(box.find('xmin').text)
                            ymin = float(box.find('ymin').text)
                            xmax = float(box.find('xmax').text)
                            ymax = float(box.find('ymax').text)
                            x, y, w, h = self.rotate_xml(
                                img, xmin, ymin, xmax, ymax, angle)
                            # change the coord
                            box.find('xmin').text = str(x)
                            box.find('ymin').text = str(y)
                            box.find('xmax').text = str(x + w)
                            box.find('ymax').text = str(y + h)
                            box.set('updated', 'yes')
                        # write into new xml
                        tree.write(xml_save_path + n + "_" + str(angle) +
                                   "d.xml")
                    except Exception:
                        # raise ValueError("no file")
                        pass
                    finally:
                        print("[%s] %s is processed." % (angle, img_name))


if __name__ == '__main__':
    img_aug = ImgAugemention()
    imgs_path = 'D:\\getPianwei\\HBXZ\\'
    xmls_path = 'D:\\getPianwei\\HBXZLabels\\'
    # imgs_path = 'D:\\getPianwei\\test\\croppedIQI\\'
    # xmls_path = 'D:\\getPianwei\\test\\IQIlabels\\'
    img_save_path = 'D:\\getPianwei\\AMEIMG\\'
    xml_save_path = 'D:\\getPianwei\\AMEXML\\'
    angle_list = [90, 180, 270]
    img_aug.process_img(imgs_path, xmls_path, img_save_path, xml_save_path,
                        angle_list)

    img_aug._process_img_flip(imgs_path, xmls_path, img_save_path,
                              xml_save_path, [1, 0, -1])
