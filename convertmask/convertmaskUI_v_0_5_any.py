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

sys.path.append('..')

import webbrowser

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QStringListModel
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog,
                             QGraphicsPixmapItem, QGraphicsScene, QMainWindow,
                             QMessageBox, qApp)
from skimage import io

from convertmask import (__appname__, __support_anno_types__,
                         __support_classfiles_types__, __support_img_types__,
                         __support_methods__, __version__)
from convertmask.UI.utils.getAllTypeFiles import getFiles

BASE_DIR = os.path.abspath(os.curdir)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # MainWindow.setObjectName("MainWindow")
        self.setWindowTitle("{} version:{}".format(__appname__, __version__))
        self.setFixedSize(1126, 901)
        self.setWindowIcon(
            QIcon(BASE_DIR + os.sep + 'UI' + os.sep + 'statics' + os.sep +
                  'look.png'))
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(160, 0, 701, 851))
        self.graphicsView.setObjectName("graphicsView")
        self.imglistView = QtWidgets.QListView(self.centralwidget)
        self.imglistView.setGeometry(QtCore.QRect(860, 0, 261, 281))
        self.imglistView.setObjectName("imglistView")
        self.labellistView = QtWidgets.QListView(self.centralwidget)
        self.labellistView.setGeometry(QtCore.QRect(860, 280, 261, 301))
        self.labellistView.setObjectName("labellistView")
        self.previous = QtWidgets.QPushButton(self.centralwidget)
        self.previous.setGeometry(QtCore.QRect(30, 740, 75, 23))
        self.previous.setObjectName("previous")
        self.next = QtWidgets.QPushButton(self.centralwidget)
        self.next.setGeometry(QtCore.QRect(30, 690, 75, 23))
        self.next.setObjectName("next")
        self.do_2 = QtWidgets.QPushButton(self.centralwidget)
        self.do_2.setGeometry(QtCore.QRect(30, 80, 75, 23))
        self.do_2.setObjectName("do_2")
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(10, 30, 131, 21))
        self.comboBox.setObjectName("comboBox")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(860, 580, 261, 271))
        self.textBrowser.setObjectName("textBrowser")
        self.setCentralWidget(self.centralwidget)

        self.imglist = []
        self.annolist = []

        openFileAction = QAction('Open Image File...', self)
        openClassInfoFileAction = QAction('Open Class Information File...', self)
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
        testAction = QAction('Test ...',self)
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
    
    def _test(self):
        # pass
        from convertmask.UI.components.augForm import AugForm
        d = AugForm(name=1,sex=2)
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
            "Class Information Files({})".format(' '.join(__support_classfiles_types__)))
        with open(fileName,'r',encoding='utf-8',errors='ignore') as f:
            txt = f.readlines()
        # self.textBrowser.
        for i in txt:
            self.textBrowser.append(i.replace('\n','')) 

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
        imgpath = self.imglist[qModelIndex.row()]
        img = io.imread(imgpath)
        x = img.shape[1]  #获取图像大小
        y = img.shape[0]
        frame = QImage(img, x, y, QImage.Format_RGB888)
        pix = QPixmap.fromImage(frame)
        self.item = QGraphicsPixmapItem(pix)  #创建像素图元
        #self.item.setScale(self.zoomscale)
        self.scene = QGraphicsScene()  #创建场景
        self.scene.addItem(self.item)
        self.graphicsView.setScene(self.scene)  #将场景添加至视图
    
    def clickAnno(self,qModelIndex):
        self.textBrowser.clear()
        annoPath = self.annolist[qModelIndex.row()]
        with open(annoPath,'r',encoding='utf-8',errors='ignore') as f:
            txt = f.readlines()
        # self.textBrowser.
        for i in txt:
            self.textBrowser.append(i.replace('\n',''))      


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    form = MainWindow()
    form.show()
    sys.exit(app.exec_())
