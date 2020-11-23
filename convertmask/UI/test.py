'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-11-18 11:31:07
LastEditors: xiaoshuyui
LastEditTime: 2020-11-18 12:21:34
'''
import sys
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication
from PyQt5.QtGui import QIcon
 
 
class Example(QMainWindow):
     
    def __init__(self):
        super().__init__()
         
        self.my_UI()
         
         
    def my_UI(self):              
         
        exitAction = QAction(QIcon('exit.png'), '&退出', self)    #QAction是一个用于菜单栏、工具栏或自定义快捷键的抽象动作行为
                                                                  #给该行为显示为退出，插入图标
        exitAction.setShortcut('Ctrl+Q')                          #为这个动作定义一个快捷键
        exitAction.setStatusTip('退出应用')                       #创建一个当我们鼠标浮于菜单项之上就会显示的一个状态提示
        exitAction.triggered.connect(qApp.quit)                   #当我们选中特定的动作，一个触发信号会被发射。信号连接到QApplication组件的quit()方法。这样就中断了应用。当我们选中特定的动作，一个触发信号会被发射。信号连接到QApplication组件的quit()方法。这样就中断了应用。
 
        self.statusBar()                                          #创建状态栏，用来显示上面的状态提示
 
        menubar = self.menuBar()                                  #menuBar()方法创建了一个菜单栏
        fileMenu = menubar.addMenu('文件&(F)')                       #创建一个文件菜单，设置快捷键F
        fileMenu.addAction(exitAction)                            #将退出动作添加到file菜单中
         
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('菜单栏')   
        self.show()
         
         
if __name__ == '__main__':
     
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())