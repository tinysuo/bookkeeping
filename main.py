import sys, os

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

sys.path.append("module")
import utils
from login import LoginDialog

import config
import mainWindow


def main():
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QCoreApplication.addLibraryPath(r'.\runtime\site-packages\PyQt5\Qt5\plugins')
    config.app_home = os.path.dirname(__file__)
    # 创建应用
    app = QApplication(sys.argv)	
    styleFile = "%s%s" % (config.app_home,'/themes/light.qss')
    with open(styleFile, 'r',encoding='UTF-8') as f:
        app.setStyleSheet(f.read())
	
    main_window = None
    # 设置登录窗口
    login_ui = LoginDialog()
    # 校验是否验证通过
    if login_ui.exec_() != QDialog.Accepted:
        os._exit(0) 
    # 展示窗口
    main_window = mainWindow.MainWindow()
    main_window.show()

    app.exec_()  
   

if __name__ == "__main__":
    main()
