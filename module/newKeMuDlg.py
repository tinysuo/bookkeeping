
import os
import sqlite3
import config
import hashlib
import uuid

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


def msgbox(title,msg):
    QMessageBox.warning(None,title,msg,QMessageBox.Ok)

def getFuZhuTypes():
    sql = "SELECT 辅助类 FROM 辅助类别表"
    cursor = config.sql_conn.cursor()
    try:
        cursor.execute(sql)
        types = cursor.fetchall()
        cursor.close
    except BaseException as e:
        msgbox("提示",str(e))
        return []
    return types

def newKeMu(uuid,type,code,name,puuid,fuzhu):
    sql = "INSERT INTO 科目表 (uuid,类别,代码,名称,父uuid,辅助) VALUES (?,?,?,?,?,?)"
    cursor = config.sql_conn.cursor()
    try:
        cursor.execute(sql,[uuid,type,code,name,puuid,fuzhu])
        cursor.close
    except BaseException as e:
        msgbox("提示",str(e))
        return
    config.sql_conn.commit()  

def modifyKeMu(uuid,code,name,fuzhu):
    sql = "UPDATE 科目表 SET 代码=?,名称=?,辅助=? WHERE uuid=?"
    cursor = config.sql_conn.cursor()
    try:
        cursor.execute(sql,[code,name,fuzhu,uuid])
        cursor.close
    except BaseException as e:
        msgbox("提示",str(e))
        return
    config.sql_conn.commit()  

class newKeMuDlg(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('新科目')  # 设置标题
        self.setGeometry(200,200,400,400)

        self.pcode=""
        self.pname =""
        self.modify = 0
        self.puuid=""
        self.uuid =""
        self.code = ""
        self.name = ""
        self.fuzhu = ""

        self.vLayout = QVBoxLayout(self)  # 设置横向布局
        self.vLayout.setContentsMargins(100,100, 100, 100)

        self.formlayout = QFormLayout()
        self.vLayout.addLayout(self.formlayout)

        self.hLayout = QHBoxLayout()
        self.escBTN = QPushButton("取消")
        self.newBTN = QPushButton("新建")
        self.hLayout.addWidget(self.escBTN)
        self.hLayout.addWidget(self.newBTN)
        self.vLayout.addLayout(self.hLayout)

        self.escBTN.clicked.connect(self.escBTNClicked)
        self.newBTN.clicked.connect(self.newBTNClicked)
        self.initFormlayout()

    def initFormlayout(self):
        #初始化表单layout
        self.typeLable=QLabel("")
        self.pnameLable=QLabel("")
        self.codeEdit = QLineEdit()
        self.nameEdit = QLineEdit()
        self.fuzhuComboBox = QComboBox()
        self.fuzhuComboBox.addItem("本科目不设置辅助核算","")
        types = getFuZhuTypes()
        for type in types:
            if type !=None:
                self.fuzhuComboBox.addItem(type[0],type[0])
        self.fuzhuComboBox.setCurrentIndex(0)

        self.formlayout.addRow("科目类别",self.typeLable)
        self.formlayout.addRow("父级科目",self.pnameLable)
        self.formlayout.addRow("科目代码",self.codeEdit)
        self.formlayout.addRow("科目名称",self.nameEdit)
        self.formlayout.addRow("辅助核算",self.fuzhuComboBox)


    def initData(self):
        self.pnameLable.setText(self.pname)
        self.typeLable.setText(self.type)
        self.codeEdit.setText(self.code)
        self.nameEdit.setText(self.name)
        self.fuzhuComboBox.setCurrentText(self.fuzhu)
        if self.modify == 1:
            self.newBTN.setText("保存")

    def escBTNClicked(self):
        self.reject()

    def newBTNClicked(self):
        code = self.codeEdit.text()
        name = self.nameEdit.text()
        fuzhu = self.fuzhuComboBox.currentData(Qt.UserRole)
        if code == "":
            msgbox("提示","科目代码不能为空")
            return
        if code.isdigit() == False:
            msgbox("提示","科目代码只能是数字")
            return
        if len(code) != 4 and self.puuid == "":
            msgbox("提示","一级科目代码只能是4位数字")
            return
        if len(code) <6 and self.puuid != "":
            msgbox("提示","二级科目之后每级加两位数字，编码方案为4-2-2")
            return
        if name == "":
            msgbox("提示","科目名称不能为空")
            return

        if self.modify == 0 :
            ret = newKeMu(self.uuid,self.type,code,name,self.puuid,fuzhu)
        elif self.modify == 1:
            ret = modifyKeMu(self.uuid,code,name,fuzhu)
        self.accept()

    