import sys, os
import threading
import time
import typing
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import hashlib

from PyQt5.QtWidgets import QWidget
import config
import json
import sqlite3

import 凭证处理
import 账套设置
import 明细查看

import urllib.request
import json
import shellexecute


class AboutDlg(QDialog):
    def __init__(self,parent, *args, **kwargs):
        super().__init__(parent,*args, **kwargs)
        #self.setWindowFlags(Qt.Popup)        
        self.setContentsMargins(30,30,30,30)
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.vLayout = QVBoxLayout(self)
        
        aboutFile = "%s%s" % (config.app_home,'/doc/about.html')
        with open(aboutFile, 'r',encoding='UTF-8') as f:
            text = f.read()
        self.textEdit = QTextEdit()
        self.textEdit.insertHtml(text)
        self.textEdit.setReadOnly(True)
        self.vLayout.addWidget( self.textEdit)

        self.setLayout(self.vLayout)
        self.formLayout = QFormLayout()
        self.hLayout = QHBoxLayout()
        self.vLayout.addLayout(self.formLayout)

        
        self.formLayout.addRow("主版本号：",QLabel("%d"%(config.major)))
        self.formLayout.addRow("次版本号：",QLabel("%d"%(config.minor)))


        btn_ok = QPushButton("确定")
        btn_ok.clicked.connect(self.onBtnOkClicked)
        self.hLayout.addWidget(btn_ok)

        self.vLayout.addLayout(self.hLayout)

    def onBtnOkClicked(self):
        self.accept()



class CornerWidget(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        #self.setFixedWidth(500)
        self.setFixedHeight(48)
        self.setContentsMargins(0,0,10, 0)
        self.hlayout = QHBoxLayout(self)
        homeBtn = QPushButton("网站")
        aboutBtn = QPushButton("关于")
        homeBtn.clicked.connect(self.onHomeBtnClicked)
        aboutBtn.clicked.connect(self.onAboutBtnClicked)

        #self.hlayout.addWidget(QPushButton("111111"))
        #self.hlayout.addWidget(QPushButton("111111"))
        self.info = QLabel("")
        self.info.setObjectName("cornerInfo")
        self.hlayout.addWidget(self.info)        
        self.hlayout.addWidget(homeBtn)
        self.hlayout.addWidget(aboutBtn)
        aboutBtn.setObjectName("aboutBtn")
        aboutBtn.setFlat(True)

        homeBtn.setObjectName("aboutBtn")
        homeBtn.setFlat(True)


    def onHomeBtnClicked(self):
        shellexecute.exec("open","https://www.bitant.net/bookkeeping/index.html","",1)
    def onAboutBtnClicked(self):
        dlg = AboutDlg(self)
        dlg.exec()




class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.setWindowTitle(config.db_name + '--蚂蚁记账')
        self.setGeometry(320,50,1430,850)

        MainWindow.setWindowIcon(self,QIcon(config.app_home+"/images/logo256.png"))

        #居中
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)
        self.showMaximized()
        
        self.nav_btns = []
  
        self.vLayout = QVBoxLayout(self)  # 设置横向布局
        self.vLayout.setContentsMargins(0,0,0, 0)
        self.vLayout.setSpacing(0)

        widget = QWidget()
        widget.setLayout(self.vLayout)
        self.setCentralWidget(widget)

        self.topLayout = QHBoxLayout()
        self.vLayout.addLayout(self.topLayout)

        self.tabwidget = QTabWidget()
        self.vLayout.addWidget(self.tabwidget)

        widget2 = 凭证处理.voucheWidget()
        widget3 = 明细查看.MSWidget()
      
        self.tabwidget.addTab(widget2,"凭证处理")
        self.tabwidget.addTab(widget3,"明细查看")
        #self.tabwidget.addTab(QWidget(),"财务报表")

        self.accountWidget =账套设置.AccountSeting() 
        self.tabwidget.addTab(self.accountWidget,"账套设置")
        self.cornerWidget = CornerWidget(self)
        self.tabwidget.setCornerWidget(self.cornerWidget)
    
        getinfo_thread = threading.Thread(target=self.showServerInfo)
        getinfo_thread.start()
        
        
    #tab(标签)关闭函数；
    def close_tab(self,index):
        self.tabwidget.removeTab(index)

    def showServerInfo(self):
        try:
            urlver = urllib.request.urlopen("https://www.bitant.net/bookkeeping/bookkeeping.json")
        except urllib.error.HTTPError as e:
            print(e.code)   # 404
        finally:
            str = urlver.read().decode('utf-8')
            jobj = json.loads(str)
            if jobj["ver"]["major"] > config.major:
                print("主版本升级了")
                self.cornerWidget.info.setText("发现新版本")
            elif jobj["ver"]["minor"] > config.minor:
                print("次版本升级了")
                




