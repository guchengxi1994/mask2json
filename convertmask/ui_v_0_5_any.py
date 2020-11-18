'''
lanhuage: python
Descripttion: deprecated
version: beta
Author: xiaoshuyui
Date: 2020-10-30 08:29:24
LastEditors: xiaoshuyui
LastEditTime: 2020-11-18 15:43:43
'''
import os
import sys
import webbrowser

sys.path.append('..')

from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow,
                             qApp)

from convertmask import __appname__, __version__

BASE_DIR = os.path.abspath(os.curdir)
# print(BASE_DIR)


class MainForm(QMainWindow):
    def __init__(self) -> None:
        super(MainForm, self).__init__()

        self.setWindowTitle("{} version:{}".format(__appname__, __version__))
        self.setFixedSize(800, 600)
        self.setWindowIcon(
            QIcon(BASE_DIR + os.sep + 'UI' + os.sep + 'statics' + os.sep +
                  'look.png'))

        openFileAction = QAction('Open File...', self)
        openFolderAction = QAction('Open Folder...', self)
        exitAction = QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        openFileAction.setShortcut('Ctrl+O')
        openFolderAction.setShortcut('Ctrl+K')

        self.statusBar()
        menubar = self.menuBar()  #menuBar()方法创建了一个菜单栏

        # file menu
        fileMenu = menubar.addMenu('File')  #创建一个文件菜单，设置快捷键F
        fileMenu.addAction(openFileAction)
        fileMenu.addAction(openFolderAction)
        fileMenu.addAction(exitAction)
        exitAction.triggered.connect(qApp.quit)
        openFileAction.triggered.connect(self.openFile)
        openFolderAction.triggered.connect(self.openFolder)

        # help menu
        helpMenu = menubar.addMenu('Help')
        helpDetails = QAction('Show Details', self)
        helpMenu.addAction(helpDetails)
        helpDetails.triggered.connect(self.showHelpInformation)
        aboutDetails = QAction('About',self)
        helpMenu.addAction(aboutDetails)
        

    def openFile(self):
        fileName, fileType = QFileDialog.getOpenFileName(
            self, "select file", os.getcwd(),
            "All Files(*);;Text Files(*.txt)")
        print(fileName)
        print(fileType)

    def openFolder(self):
        dir_path = QFileDialog.getExistingDirectory(self, "select folder",
                                                    os.getcwd())
        print(dir_path)

    def showHelpInformation(self):
        url = 'https://github.com/guchengxi1994/mask2json/tree/test'
        webbrowser.open(url)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    form = MainForm()
    form.show()
    sys.exit(app.exec_())
