'''
基于PCA的图像降维及重构
'''

import numpy as np
import cv2 as cv


#数据中心化
def Z_centered(dataMat):
    rows, cols = dataMat.shape
    meanVal = np.mean(dataMat, axis=0)  # 按列求均值，即求各个特征的均值
    meanVal = np.tile(meanVal, (rows, 1))
    newdata = dataMat - meanVal
    return newdata, meanVal


#最小化降维造成的损失，确定k
def Percentage2n(eigVals, percentage):
    sortArray = np.sort(eigVals)  # 升序
    sortArray = sortArray[-1::-1]  # 逆转，即降序
    arraySum = sum(sortArray)
    tmpSum = 0
    num = 0
    for i in sortArray:
        tmpSum += i
        num += 1
        if tmpSum >= arraySum * percentage:
            return num


#得到最大的k个特征值和特征向量
def EigDV(covMat, p):
    D, V = np.linalg.eig(covMat)  # 得到特征值和特征向量
    k = Percentage2n(D, p)  # 确定k值
    print("保留99%信息，降维后的特征个数：" + str(k) + "\n")
    eigenvalue = np.argsort(D)
    K_eigenValue = eigenvalue[-1:-(k + 1):-1]
    K_eigenVector = V[:, K_eigenValue]
    return K_eigenValue, K_eigenVector


#得到降维后的数据
def getlowDataMat(DataMat, K_eigenVector):
    return DataMat * K_eigenVector


#重构数据
def Reconstruction(lowDataMat, K_eigenVector, meanVal):
    reconDataMat = lowDataMat * K_eigenVector.T + meanVal
    return reconDataMat


#PCA算法
def PCA(data, p):
    dataMat = np.float32(np.mat(data))
    #数据中心化
    dataMat, meanVal = Z_centered(dataMat)
    #计算协方差矩阵
    covMat = np.cov(dataMat, rowvar=0)
    #得到最大的k个特征值和特征向量
    D, V = EigDV(covMat, p)
    #得到降维后的数据
    lowDataMat = getlowDataMat(dataMat, V)
    #重构数据
    reconDataMat = Reconstruction(lowDataMat, V, meanVal)
    return reconDataMat


def main():
    imagePath = 'C:\\Users\\xiaoshuyui\\Desktop\\108.png'
    image = cv.imread(imagePath)
    image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    rows, cols = image.shape
    print("降维前的特征个数:" + str(cols) + "\n")
    print('----------------------------------------')
    reconImage = PCA(image, 0.99)
    reconImage = reconImage.astype(np.uint8)
    cv.imshow('test', reconImage)
    cv.waitKey(0)
    cv.destroyAllWindows()


if __name__ == '__main__':
    main()
