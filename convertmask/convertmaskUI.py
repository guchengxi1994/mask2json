'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-11-18 15:30:45
LastEditors: xiaoshuyui
LastEditTime: 2020-11-19 10:42:38
'''

import json
import os
import sys
import traceback

sys.path.append('..')

import webbrowser

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QStringListModel
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog,
                             QGraphicsPixmapItem, QGraphicsScene, QHBoxLayout,
                             QLabel, QMainWindow, QMessageBox, QPushButton,
                             QVBoxLayout, QWidget, qApp)
from skimage import io

from convertmask import (__appname__, __reserved_methods__,
                         __support_anno_types__, __support_classfiles_types__,
                         __support_img_types__, __support_methods__,
                         __version__)
from convertmask.UI.utils import __UI_NAME__, __UI_VERSION__
from convertmask.UI.utils.get_all_type_files import getFiles
from convertmask.utils.auglib.operator_without_label import \
    MainOperatorWithoutLabel
from convertmask.utils.methods.img2base64 import img_b64_to_arr

BASE_DIR = os.path.abspath(os.curdir)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.__currentImgIndex = -1
        self.setWindowTitle("{} , UI version : {}".format(
            __UI_NAME__, __UI_VERSION__))
        self.setMinimumSize(960, 600)
        self.setWindowIcon(
            QIcon(BASE_DIR + os.sep + 'UI' + os.sep + 'statics' + os.sep +
                  'look.png'))
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.graphicsView = QtWidgets.QGraphicsView()
        self.graphicsView.setObjectName("graphicsView")

        self.subGraphicsView = QtWidgets.QGraphicsView()
        self.subGraphicsView.setObjectName("subGraphicsView")

        self.imglistView = QtWidgets.QListView()
        self.imglistView.setObjectName("imglistView")

        self.subImgListView = QtWidgets.QListView(
        )  # augmentation, mask imgs list
        self.subImgListView.setObjectName("subImgListView")

        self.labellistView = QtWidgets.QListView()
        self.labellistView.setObjectName("labellistView")

        self.previous = QtWidgets.QPushButton()
        self.previous.setObjectName("previous")
        self.previous.clicked.connect(self.previousAction)
        self.next = QtWidgets.QPushButton()
        self.next.setObjectName("next")
        self.next.clicked.connect(self.nextAction)
        self.do_2 = QtWidgets.QPushButton()
        self.do_2.setObjectName("do_2")
        self.do_2.clicked.connect(self.__execAction)

        self.comboBox = QtWidgets.QComboBox()
        self.comboBox.setObjectName("comboBox")
        self.textBrowser = QtWidgets.QTextBrowser()
        self.textBrowser.setObjectName("textBrowser")

        self.textClassBrowser = QtWidgets.QTextBrowser()
        self.textClassBrowser.setObjectName("textClassBrowser")

        self.mainLayout = QHBoxLayout()

        self.leftSideButtonGroup = QVBoxLayout()
        self.leftSideButtonGroup.addWidget(self.comboBox)
        self.leftSideButtonGroup.addWidget(self.previous)
        self.leftSideButtonGroup.addWidget(self.next)
        self.leftSideButtonGroup.addWidget(self.do_2)

        self.rightWidgetGroup = QVBoxLayout()

        __oriImgLayout = QVBoxLayout()
        __oriImgLayout.addWidget(QLabel("origin images"))
        __oriImgLayout.addWidget(self.imglistView)
        imgListViewLayout = QHBoxLayout()
        imgListViewLayout.addLayout(__oriImgLayout)

        __subImgLayout = QVBoxLayout()
        __subImgLayout.addWidget(QLabel("mask/augmented images"))
        __subImgLayout.addWidget(self.subImgListView)
        imgListViewLayout.addLayout(__subImgLayout)

        self.rightWidgetGroup.addLayout(imgListViewLayout)

        __annoListLayout = QVBoxLayout()
        __annoListLayout.addWidget(QLabel("annotation list"))
        __annoListLayout.addWidget(self.labellistView)

        self.rightWidgetGroup.addLayout(__annoListLayout)

        browserLayout = QHBoxLayout()

        __textLayout = QVBoxLayout()
        __textLayout.addWidget(QLabel("annotation"))
        __textLayout.addWidget(self.textBrowser)

        __textClassLayout = QVBoxLayout()
        __textClassLayout.addWidget(QLabel("classes"))
        __textClassLayout.addWidget(self.textClassBrowser)

        browserLayout.addLayout(__textLayout)
        browserLayout.addLayout(__textClassLayout)

        # self.rightWidgetGroup.addWidget(self.textBrowser)
        self.rightWidgetGroup.addLayout(browserLayout)

        __imgViewLayout = QVBoxLayout()
        __imgViewLayout.addWidget(QLabel("origin image"))
        __imgViewLayout.addWidget(self.graphicsView)
        __imgViewLayout.addWidget(QLabel("mask/augmented image"))
        __imgViewLayout.addWidget(self.subGraphicsView)

        self.mainLayout.addLayout(self.leftSideButtonGroup)
        self.mainLayout.addLayout(__imgViewLayout)
        self.mainLayout.addLayout(self.rightWidgetGroup)

        self.centralwidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.centralwidget)

        self.imglist = []
        self.annolist = []

        openFileAction = QAction('Open Image File...', self)
        openClassInfoFileAction = QAction('Open Class Information File...',
                                          self)
        openImageFolderAction = QAction('Open Image Folder...', self)
        openAnnotationFolderAction = QAction('Open Annotation Folder...', self)
        exitAction = QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        openFileAction.setShortcut('Ctrl+O')
        openImageFolderAction.setShortcut('Ctrl+K')
        openAnnotationFolderAction.setShortcut('Ctrl+L')
        openClassInfoFileAction.setShortcut('Ctrl+J')

        self.statusBar()
        menubar = self.menuBar()  #menuBar()方法创建了一个菜单栏

        # file menu
        fileMenu = menubar.addMenu('File')  #创建一个文件菜单，设置快捷键F
        fileMenu.addAction(openFileAction)
        fileMenu.addAction(openImageFolderAction)
        fileMenu.addAction(openAnnotationFolderAction)
        fileMenu.addAction(openClassInfoFileAction)
        fileMenu.addAction(exitAction)
        # do actions
        exitAction.triggered.connect(qApp.quit)
        openFileAction.triggered.connect(self.openImgFile)
        openImageFolderAction.triggered.connect(self.openImgFolder)
        openAnnotationFolderAction.triggered.connect(self.openAnnoFolder)
        openClassInfoFileAction.triggered.connect(self.openClassInfo)

        # change
        changeAction = QAction('Change mask/augmented image folder', self)
        changeMenu = menubar.addMenu("Change")
        changeMenu.addAction(changeAction)
        changeMenu.triggered.connect(self.__changeMaskFolder)

        # test menu
        testAction = QAction('Test ...', self)
        testMenu = menubar.addMenu('Test')
        testMenu.addAction(testAction)
        testAction.setShortcut('Ctrl+T')
        testAction.triggered.connect(self._test)

        # help menu
        helpMenu = menubar.addMenu('Help')
        helpDetails = QAction('Show Details', self)
        helpMenu.addAction(helpDetails)
        helpDetails.triggered.connect(self.showHelpInformation)
        aboutDetails = QAction('About', self)
        helpMenu.addAction(aboutDetails)

        # ori image
        self.slm = QStringListModel()
        # mask image
        self.subSlm = QStringListModel()
        # annotation json/xml list
        self.annoSlm = QStringListModel()

        QtCore.QMetaObject.connectSlotsByName(self)

        _translate = QtCore.QCoreApplication.translate
        # self.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.previous.setText(_translate("MainWindow", "previous"))
        self.next.setText(_translate("MainWindow", "next"))
        self.do_2.setText(_translate("MainWindow", "DO!"))

        self.comboBox.addItems(__support_methods__)
        self.imglistView.clicked.connect(self.clickImg)
        self.labellistView.clicked.connect(self.clickAnno)
        self.subImgListView.clicked.connect(self.clickSubImgList)

        # yaml or txt path
        self.__labelPath = ""
        self.__subImgList = []
        self.__subImgFolder = ''
        self.comboBox.currentIndexChanged.connect(self.__indexChangedAction)
        self.__augs = ''
        self.__currentAnnoIndex = -1

    def __indexChangedAction(self):
        # print(self.comboBox.currentText())
        if self.comboBox.currentText() == "augmentation":
            from convertmask.UI.components.augment_form import AugForm
            d = AugForm()
            d.exec_()
            print(d.chosenMethod.text())
            self.__augs = d.chosenMethod.text()

    def getMaskImgPath(self, imgpath: str) -> str:
        try:
            _fp, _ = os.path.split(imgpath)
            __tmp = imgpath.replace(_fp, self.__subImgFolder).split(".")[0]
            __file = list(filter(lambda x: __tmp in x, self.__subImgList))[0]
            return __file
        except:
            return ""

    def __execAction(self):
        if self.comboBox.currentText() == "mask2json":
            if len(self.imglist) == 0:
                return
            print(self.imglist[self.__currentImgIndex])
            if self.textClassBrowser.toPlainText() == "":
                self.openClassInfo()
            a = self.getMaskImgPath(self.imglist[self.__currentImgIndex])
            if a == "":
                return
            from convertmask.utils.methods import getMultiShapes
            _j = getMultiShapes.getMultiShapes(
                self.imglist[self.__currentImgIndex],
                a,
                os.getcwd(),
                self.__labelPath,
                flag=True)
            self.textBrowser.setText(_j)

        if self.comboBox.currentText() == "augmentation":
            if len(self.imglist) == 0:
                return
            print(self.imglist[self.__currentImgIndex])
            try:
                _p = BASE_DIR + os.sep + 'test_imgs' + os.sep + "cache"
                # print(BASE_DIR + os.sep + 'test_imgs' + os.sep + "cache")
                imgpath = self.imglist[self.__currentImgIndex]
                _operators = MainOperatorWithoutLabel(imgpath,
                                                      saveDir=_p,
                                                      saveFile=True)
                _operators.augs = self.__augs.split(";")
                _operators.autoAugment()

                self.__subImgFolder = _p
                subRes = getFiles(_p, __support_img_types__)
                qSubList = subRes
                self.subSlm.setStringList(qSubList)
                self.__subImgList = qSubList
                self.subImgListView.setModel(self.subSlm)
                self.__updateSubImage(self.__subImgList[0])

            except:
                traceback.print_exc()

        if self.comboBox.currentText() == "json2mask":
            try:
                _p = BASE_DIR + os.sep + 'test_imgs' + os.sep + "cache"
                from convertmask.utils.json2mask.convert_with_label import \
                    processor
                annoPath = self.annolist[self.__currentAnnoIndex]
                print(annoPath)
                _jsonData = json.load(open(annoPath))
                array = img_b64_to_arr(_jsonData.get("imageData"))
                self.__updateImage("",array)

                if self.__labelPath == "" or self.__labelPath is None:
                    QMessageBox.warning(
                        self, "Warning",
                        "Json to mask without yamls is not recommended.",
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                    return
                path = processor(annoPath, self.__labelPath)
                viz = getFiles(path + os.sep+ "mask_viz" + os.sep,__support_img_types__)
                self.subSlm.setStringList(viz)
                self.__subImgList = viz
                self.subImgListView.setModel(self.subSlm)
                self.__updateSubImage(self.__subImgList[0])
                
            except:
                traceback.print_exc()

    def nextAction(self):
        if self.__currentImgIndex == -1 or self.__currentImgIndex + 1 == len(
                self.imglist):
            return
        self.__updateImage(self.imglist[self.__currentImgIndex + 1])
        self.__currentImgIndex += 1
        self.imglistView.setCurrentIndex(self.slm.index(
            self.__currentImgIndex))

    def previousAction(self):
        if self.__currentImgIndex == -1 or self.__currentImgIndex == 0:
            return
        self.__updateImage(self.imglist[self.__currentImgIndex - 1])
        self.__currentImgIndex -= 1
        self.imglistView.setCurrentIndex(self.slm.index(
            self.__currentImgIndex))

    def _test(self):
        # pass
        from convertmask.UI.components.augment_form import AugForm
        d = AugForm(name=1, sex=2)
        d.exec_()

    def openImgFile(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self, "select file", os.getcwd(),
            "Image Files({})".format(' '.join(__support_img_types__)))
        if fileName is None or fileName == "":
            return
        qlist = [fileName]
        self.slm.setStringList(qlist)
        self.imglist = qlist
        self.__currentImgIndex = 0
        self.imglistView.setModel(self.slm)
        self.imglistView.setCurrentIndex(self.slm.index(
            self.__currentImgIndex))
        self.__updateImage(self.imglist[self.__currentImgIndex])

    def openClassInfo(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self, "select file", os.getcwd(),
            "Class Information Files({})".format(
                ' '.join(__support_classfiles_types__)))

        if os.path.exists(fileName):
            self.__labelPath = fileName
            with open(fileName, 'r', encoding='utf-8', errors='ignore') as f:
                txt = f.readlines()
            # self.textBrowser.
            for i in txt:
                self.textClassBrowser.append(i.replace('\n', ''))

    def __changeMaskFolder(self):
        dir_path = QFileDialog.getExistingDirectory(
            self, "select mask image folder (or just pass)", os.getcwd())
        self.__subImgFolder = dir_path
        subRes = getFiles(dir_path, __support_img_types__)
        qSubList = subRes
        self.subSlm.setStringList(qSubList)
        self.__subImgList = qSubList
        self.subImgListView.setModel(self.subSlm)

    def openImgFolder(self):
        dir_path = QFileDialog.getExistingDirectory(
            self, "select origin image folder", os.getcwd())
        # print(dir_path)
        res = getFiles(dir_path, __support_img_types__)
        # print(res)
        # slm = QStringListModel()
        qlist = res
        # qSubList = list(filter(lambda x:"_mask"  in x,res))
        if self.__subImgFolder == "" and self.comboBox.currentText(
        ) in __reserved_methods__:
            dir_path = QFileDialog.getExistingDirectory(
                self, "select mask image folder (or just pass)", os.getcwd())
            self.__subImgFolder = dir_path
        subRes = getFiles(dir_path, __support_img_types__)
        qSubList = subRes

        self.slm.setStringList(qlist)
        self.subSlm.setStringList(qSubList)
        self.imglist = qlist
        self.__subImgList = qSubList
        self.imglistView.setModel(self.slm)
        self.subImgListView.setModel(self.subSlm)
        if len(self.imglist)>0:
            self.__currentImgIndex = 0
            self.imglistView.setCurrentIndex(self.slm.index(
                self.__currentImgIndex))
            self.__updateImage(self.imglist[self.__currentImgIndex])
            try:
                _fp, _ = os.path.split(self.imglist[self.__currentImgIndex])
                __tmp = self.imglist[self.__currentImgIndex].replace(
                    _fp, self.__subImgFolder).split(".")[0]
                __file = list(filter(lambda x: __tmp in x, self.__subImgList))[0]
                self.__updateSubImage(__file)
                index = self.__subImgList.index(__file)
                self.subImgListView.setCurrentIndex(self.subSlm.index(index))
            except:
                self.subGraphicsView.setScene(None)

    def openAnnoFolder(self):
        dir_path = QFileDialog.getExistingDirectory(
            self, "select annotation folder", os.getcwd())
        res = getFiles(dir_path, __support_anno_types__)
        # print(res)
        # slm = QStringListModel()
        qlist = res
        self.annoSlm.setStringList(qlist)
        self.annolist = qlist
        self.labellistView.setModel(self.annoSlm)

    def showHelpInformation(self):
        url = 'https://github.com/guchengxi1994/mask2json/tree/test'
        webbrowser.open(url)

    def clickImg(self, qModelIndex):
        imgpath = self.imglist[qModelIndex.row()]
        self.__currentImgIndex = qModelIndex.row()
        self.__updateImage(imgpath)
        _fp, _ = os.path.split(imgpath)
        __tmp = imgpath.replace(_fp, self.__subImgFolder).split(".")[0]
        # print(__tmp)
        try:
            __file = list(filter(lambda x: __tmp in x, self.__subImgList))[0]
            self.__updateSubImage(__file)
            index = self.__subImgList.index(__file)
            self.subImgListView.setCurrentIndex(self.subSlm.index(index))
        except:
            self.subGraphicsView.setScene(None)

    def clickSubImgList(self, qModelIndex):
        if self.comboBox.currentText() != "augmentation":
            return
        imgpath = self.__subImgList[qModelIndex.row()]
        self.__updateSubImage(imgpath)
        index = self.__subImgList.index(imgpath)
        self.subImgListView.setCurrentIndex(self.subSlm.index(index))

    def __updateImage(self, imgpath: str,imgArray=None):
        if imgArray is  None:   
            img = io.imread(imgpath)
        else:
            img = imgArray
        # print(img.shape)
        x = img.shape[1]  #获取图像大小
        y = img.shape[0]
        if len(img.shape) == 2:
            import cv2
            img = cv2.merge([img, img, img])
        frame = QImage(img, x, y, QImage.Format_RGB888)
        pix = QPixmap.fromImage(frame)
        self.item = QGraphicsPixmapItem(pix)  #创建像素图元
        #self.item.setScale(self.zoomscale)
        self.scene = QGraphicsScene()  #创建场景
        self.scene.addItem(self.item)
        self.graphicsView.setScene(self.scene)  #将场景添加至视图

    def __updateSubImage(self, imgpath: str):
        img = io.imread(imgpath)
        # print(img.shape)
        x = img.shape[1]  #获取图像大小
        y = img.shape[0]
        if len(img.shape) == 2:
            import cv2
            img = cv2.merge([img, img, img])
        frame = QImage(img, x, y, QImage.Format_RGB888)
        pix = QPixmap.fromImage(frame)
        self.item = QGraphicsPixmapItem(pix)  #创建像素图元
        #self.item.setScale(self.zoomscale)
        self.scene = QGraphicsScene()  #创建场景
        self.scene.addItem(self.item)
        self.subGraphicsView.setScene(self.scene)  #将场景添加至视图

    def clickAnno(self, qModelIndex):
        self.textBrowser.clear()
        self.__currentAnnoIndex = qModelIndex.row()
        annoPath = self.annolist[qModelIndex.row()]
        with open(annoPath, 'r', encoding='utf-8', errors='ignore') as f:
            txt = f.readlines()
        # self.textBrowser.
        for i in txt:
            self.textBrowser.append(i.replace('\n', ''))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    form = MainWindow()
    form.show()
    sys.exit(app.exec_())
