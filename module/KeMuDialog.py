import sys, os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import hashlib
import config
import json
import sqlite3
import utils
from dbfunc import *

class KeMuDialog(QDialog):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.result = [0,"","",""]
        self.setWindowTitle('选择科目')  # 设置标题
        self.setGeometry(500,200,400,600)
        self.vLayout = QVBoxLayout(self)  # 设置横向布局
        self.vLayout.setContentsMargins(20,20, 20, 20)
        #self.vLayout.addStretch(1)
        self.vLayout.setSpacing(5)

        self.kemuTreeWidget = QTreeWidget()
        utils.initKeMuTreeWidget(self.kemuTreeWidget)
        
        self.vLayout.addWidget(self.kemuTreeWidget)

        hLayout1 = QHBoxLayout()
        self.fuzhuComboBox = QComboBox()
        hLayout1.addWidget(QLabel("辅助核算:"))
        hLayout1.addWidget(self.fuzhuComboBox)
        hLayout1.setStretch(1,3)

        hLayout2 = QHBoxLayout()
        self.vLayout.addLayout(hLayout1)
        self.vLayout.addLayout(hLayout2)
        yesBtn = QPushButton("确定")
        escBtn = QPushButton("取消")
        hLayout2.addStretch(1)
        hLayout2.addWidget(yesBtn)
        hLayout2.addWidget(escBtn)
        yesBtn.clicked.connect(self.yesBntClicked)
        escBtn.clicked.connect(self.escBntClicked)

        self.kemuTreeWidget.itemDoubleClicked.connect(self.itemDoubleClicked)
        self.kemuTreeWidget.itemClicked.connect(self.itemClicked)


    def itemClicked(self,item):
        if item.parent() == None:
            return
        n = item.childCount()
        if(n == 0):            
            self.result[0] = item.data(0,Qt.UserRole)[0]
            #还需要判断科目没有挂辅助
            fz_items = getKemuFuzhu(self.result[0])
            if fz_items[0] == 1:#没有挂辅助可以直接返回
                self.fuzhuComboBox.clear()
                self.fuzhuComboBox.addItem("当前分录不设置辅助","")
                for fz in fz_items[1]:
                    self.fuzhuComboBox.addItem(fz,fz)

    def itemDoubleClicked(self,item:QTreeWidgetItem,col:int):
        if item.parent() == None:
            return
        n = item.childCount()
        if(n == 0):
            self.result[0] = item.data(0,Qt.UserRole)[0]
            #还需要判断科目没有挂辅助
            fz_items = getKemuFuzhu(self.result[0])
            if fz_items[0] == 0:#没有挂辅助可以直接返回
                self.accept()
            else:
                self.fuzhuComboBox.clear()
                self.fuzhuComboBox.addItem("当前分录不设置辅助","")
                for fz in fz_items[1]:
                    self.fuzhuComboBox.addItem(fz,fz)
    def yesBntClicked(self):
        item = self.kemuTreeWidget.currentItem()
        if item == None:
            return
        n = item.childCount()
        if n>0:
            return
        self.result[0] = item.data(0,Qt.UserRole)[0]
        self.result[1] = self.fuzhuComboBox.currentData(Qt.UserRole)
        self.accept()

    def escBntClicked(self):
        self.reject()




