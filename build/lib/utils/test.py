'''
@lanhuage: python
@Descripttion: 
@version: beta
@Author: xiaoshuyui
@Date: 2020-06-08 17:19:21
@LastEditors: xiaoshuyui
@LastEditTime: 2020-06-09 17:29:19
'''
import cv2


def get_approx(img, contour, length_p=0.1):
    """获取逼近多边形

    :param img: 处理图片
    :param contour: 连通域
    :param length_p: 逼近长度百分比
    """
    img_adp = img.copy()

    # 逼近长度计算
    epsilon = length_p * cv2.arcLength(contour, True)

    # 获取逼近多边形
    approx = cv2.approxPolyDP(contour, epsilon, True)

    # 绘制显示多边形
    # cv2.drawContours(img_adp, [approx], 0, (0, 0, 255), 2)
    print(approx)

    # cv2.imshow("result %.5f" % length_p, img_adp)


def main():

    # 1.导入图片, 显示原始图片
    img_src = cv2.imread("D:\\testALg\mask2json\mask2json\static\\1-2cvt.png")
    # cv2.imshow("img_src", img_src)

    # 2.灰度化,二值化
    if len(img_src.shape) == 3:
        img_gray = cv2.cvtColor(img_src, cv2.COLOR_BGR2GRAY)
    else:
        img_gray = img_src
    ret, img_bin = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY)

    # 3.连通域分析
    img_bin, contours, hierarchy = cv2.findContours(img_bin,
                                                    cv2.RETR_LIST,
                                                    cv2.CHAIN_APPROX_SIMPLE)

    # 4.获取不同尺度的逼近多边形
    # get_approx(img_src, contours[0], 0.15)
    # get_approx(img_src, contours[0], 0.09)
    # get_approx(img_src, contours[0], 0.05)
    # get_approx(img_src, contours[0], 0.02)
    get_approx(img_src, contours[0], 0.002)

    # cv2.waitKey()
    # cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
