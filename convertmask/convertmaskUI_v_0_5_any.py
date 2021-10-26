'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-11-18 15:30:45
LastEditors: xiaoshuyui
LastEditTime: 2020-11-19 10:42:38
'''

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
                             QMainWindow, QMessageBox, QVBoxLayout, QWidget,
                             qApp)
from skimage import io

from convertmask import (__appname__, __support_anno_types__,
                         __support_classfiles_types__, __support_img_types__,
                         __support_methods__, __version__)
from convertmask.UI.utils.getAllTypeFiles import getFiles
from convertmask.UI.utils import __UI_VERSION__, __UI_NAME__

BASE_DIR = os.path.abspath(os.curdir)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.__currentImgIndex = -1
        self.setWindowTitle("{} , UI version : {}".format(
            __appname__, __UI_VERSION__))
        self.setMinimumSize(960, 600)
        self.setWindowIcon(
            QIcon(BASE_DIR + os.sep + 'UI' + os.sep + 'statics' + os.sep +
                  'look.png'))
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.graphicsView = QtWidgets.QGraphicsView()
        self.graphicsView.setObjectName("graphicsView")
        self.imglistView = QtWidgets.QListView()
        self.imglistView.setObjectName("imglistView")
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
        self.rightWidgetGroup.addWidget(self.imglistView)
        self.rightWidgetGroup.addWidget(self.labellistView)

        browserLayout = QHBoxLayout()
        browserLayout.addWidget(self.textBrowser)
        browserLayout.addWidget(self.textClassBrowser)

        # self.rightWidgetGroup.addWidget(self.textBrowser)
        self.rightWidgetGroup.addLayout(browserLayout)

        self.mainLayout.addLayout(self.leftSideButtonGroup)
        self.mainLayout.addWidget(self.graphicsView)
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

        self.slm = QStringListModel()

        QtCore.QMetaObject.connectSlotsByName(self)

        _translate = QtCore.QCoreApplication.translate
        # self.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.previous.setText(_translate("MainWindow", "previous"))
        self.next.setText(_translate("MainWindow", "next"))
        self.do_2.setText(_translate("MainWindow", "DO!"))

        self.comboBox.addItems(__support_methods__)
        self.imglistView.clicked.connect(self.clickImg)
        self.labellistView.clicked.connect(self.clickAnno)

        self.__labelPath = ""

    def __execAction(self):
        # print(self.comboBox.currentText())
        if len(self.imglist) == 0:
            return
        print(self.imglist[self.__currentImgIndex])
        # print(self.textClassBrowser.toPlainText()=="")
        if self.textClassBrowser.toPlainText() == "":
            self.openClassInfo()
        print(self.__labelPath)
        if self.comboBox.currentText() == "mask2json":
            from convertmask.utils.methods import getMultiShapes
            _j = getMultiShapes.getMultiShapes(
                self.imglist[self.__currentImgIndex],
                self.imglist[self.__currentImgIndex],
                os.getcwd(),
                self.__labelPath,
                flag=True)
            # print(_j)
            self.textBrowser.setText(_j)

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
        from convertmask.UI.components.augForm import AugForm
        d = AugForm(name=1, sex=2)
        d.exec_()

    def openImgFile(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self, "select file", os.getcwd(),
            "Image Files({})".format(' '.join(__support_img_types__)))
        # slm = QStringListModel()
        qlist = [fileName]
        self.slm.setStringList(qlist)
        self.imglist = qlist
        self.imglistView.setModel(self.slm)

    def openClassInfo(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self, "select file", os.getcwd(),
            "Class Information Files({})".format(
                ' '.join(__support_classfiles_types__)))
        self.__labelPath = fileName
        with open(fileName, 'r', encoding='utf-8', errors='ignore') as f:
            txt = f.readlines()
        # self.textBrowser.
        for i in txt:
            self.textClassBrowser.append(i.replace('\n', ''))

    def openImgFolder(self):
        dir_path = QFileDialog.getExistingDirectory(self, "select folder",
                                                    os.getcwd())
        # print(dir_path)
        res = getFiles(dir_path, __support_img_types__)
        # print(res)
        # slm = QStringListModel()
        qlist = res
        self.slm.setStringList(qlist)
        self.imglist = qlist
        self.imglistView.setModel(self.slm)
        self.__currentImgIndex = 0
        self.imglistView.setCurrentIndex(self.slm.index(
            self.__currentImgIndex))
        self.__updateImage(self.imglist[self.__currentImgIndex])

    def openAnnoFolder(self):
        dir_path = QFileDialog.getExistingDirectory(self, "select folder",
                                                    os.getcwd())
        res = getFiles(dir_path, __support_anno_types__)
        # print(res)
        # slm = QStringListModel()
        qlist = res
        self.slm.setStringList(qlist)
        self.annolist = qlist
        self.labellistView.setModel(self.slm)

    def showHelpInformation(self):
        url = 'https://github.com/guchengxi1994/mask2json/tree/test'
        webbrowser.open(url)

    def clickImg(self, qModelIndex):
        try:
            imgpath = self.imglist[qModelIndex.row()]
            self.__currentImgIndex = qModelIndex.row()
            self.__updateImage(imgpath)
        except:
            traceback.print_exc()

    def __updateImage(self, imgpath: str):
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
        self.graphicsView.setScene(self.scene)  #将场景添加至视图

    def clickAnno(self, qModelIndex):
        self.textBrowser.clear()
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
