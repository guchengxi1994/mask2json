'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-11-19 09:36:38
LastEditors: xiaoshuyui
LastEditTime: 2020-11-19 10:42:49
'''
import copy
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from convertmask import (__support_aug_methods__,
                         __support_aug_optional_methods__)
from PyQt5.QtWidgets import (QComboBox, QCompleter, QDialog, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QSizePolicy,
                             QSpacerItem)


class AugForm(QDialog):
    def __init__(self,**params) -> None:
        super().__init__()
        BASE_DIR = os.path.abspath(os.curdir)
        layout = QHBoxLayout(self)
        # print(params) # test
        self.setWindowFlags( Qt.WindowCloseButtonHint)

        self.setWindowTitle(params.get("title","Augmentation"))
        self.setWindowIcon(QIcon(BASE_DIR + os.sep + 'UI' + os.sep + 'statics' + os.sep +
                  'look.png'))

        self.setFixedSize(1100, 200)

        self.chosenMethod = QLineEdit(self)
        self.chosenMethod.setFixedWidth(950)
        self.chosenMethod.move(10, 30)

        self.methods = QComboBox(self, minimumWidth=350)
        self.optional_methods = QComboBox(self, minimumWidth=350)

        self.methods.setEditable(True)
        self.optional_methods.setEditable(True)

        # layout.addWidget(self.chosenMethod)
        layout.addWidget(QLabel("Supported Methods", self))
        layout.addWidget(self.methods)
        layout.addItem(
            QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout.addWidget(QLabel("Optional Methods", self))
        layout.addWidget(self.optional_methods)

        self.commit = QPushButton(self)
        self.commit.setText('OK !')
        self.commit.clicked.connect(self.__commitAction)
        layout.addItem(
            QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout.addWidget(self.commit)

        self.initCompleter()

        self.methods.currentTextChanged.connect(self.choseCombobox)
        self.optional_methods.currentTextChanged.connect(self.choseCombobox)

    def __commitAction(self):
        self.close()

    def initCompleter(self):
        tmp = copy.deepcopy(__support_aug_methods__)
        tmp.insert(0, 'Please Choose...')
        for i in range(len(tmp)):
            self.methods.addItem(tmp[i])

        completer1 = QCompleter(__support_aug_methods__)
        completer1.setFilterMode(Qt.MatchContains)
        completer1.setCompletionMode(QCompleter.PopupCompletion)
        self.methods.setCompleter(completer1)

        tmp = copy.deepcopy(__support_aug_optional_methods__)
        tmp.insert(0, 'Please Choose...')
        for i in range(len(tmp)):
            self.optional_methods.addItem(tmp[i])

        completer2 = QCompleter(__support_aug_optional_methods__)
        completer2.setFilterMode(Qt.MatchContains)
        completer2.setCompletionMode(QCompleter.PopupCompletion)
        self.optional_methods.setCompleter(completer2)

        del tmp

    def choseCombobox(self):
        # print()
        if self.optional_methods.currentText(
        ) != 'Please Choose...' and self.optional_methods.currentText(
        ) not in self.chosenMethod.text():
            if self.chosenMethod.text() == '':
                self.chosenMethod.setText(self.optional_methods.currentText())
            else:
                self.chosenMethod.setText(self.chosenMethod.text() + ';' +
                                          self.optional_methods.currentText())

        if self.methods.currentText(
        ) != 'Please Choose...' and self.methods.currentText(
        ) not in self.chosenMethod.text():
            if self.chosenMethod.text() == '':
                self.chosenMethod.setText(self.methods.currentText())
            else:
                self.chosenMethod.setText(self.chosenMethod.text() + ';' +
                                          self.methods.currentText())
