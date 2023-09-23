import os
import sqlite3
import config
import datetime

from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

def msgbox(title,msg):
    QMessageBox.warning(None,title,msg,QMessageBox.Ok)


def newFreeDuration():
    aaa = 0
def newMonthDuration():
    aaa = 0

#新建辅助类别 
def newFuzhuType(type:str,desc:str):
    sql = "INSERT INTO 辅助类别表 (辅助类,说明) VALUES (?,?)"
    conn = config.sql_conn
    try:
        cursor = conn.cursor()
        cursor.execute(sql,[type,desc])
        cursor.close()
        conn.commit()
    except BaseException as e:
        QMessageBox.warning(None,"提示",str(e),QMessageBox.Ok)
        return -1
    return 0
#新辅助项
def newFuzhuItem(type:str,item:str,desc:str):
    sql = "INSERT INTO 辅助项目表 (类别,辅助,说明) VALUES (?,?,?)"
    conn = config.sql_conn
    try:
        cursor = conn.cursor()
        cursor.execute(sql,[type,item,desc])
        cursor.close()
        conn.commit()
    except BaseException as e:
        QMessageBox.warning(None,"提示",str(e),QMessageBox.Ok)
        return -1
    return 0    
#删除辅助类别
def delFuzhuType(type:str):
    print("111111111111111")
    n = fuzhuTypeIsUsed(type)
    if n != 0:
        msgbox("提示","有辅助项的类别不能删除，请先删除辅助项")
        return
    sql = "DELETE FROM 辅助类别表 WHERE 辅助类=?"
    conn = config.sql_conn
    try:
        cursor = conn.cursor()
        cursor.execute(sql,[type])
        cursor.close()
        conn.commit()
    except BaseException as e:
        msgbox("提示",str(e))
        return -1
#删除辅助项
def delFuzhuItem(item:str):
    print("2222222222222222")
    n = fuzhuItemIsUsed(item)
    if n != 0:
        msgbox("提示","正在使用的辅助项不能删除")
        return
    sql = "DELETE FROM 辅助项目表 WHERE 辅助=?"
    conn = config.sql_conn
    try:
        cursor = conn.cursor()
        cursor.execute(sql,[item])
        cursor.close()
        conn.commit()
    except BaseException as e:
        msgbox("提示",str(e))
        return -1
#辅助项是否在用
def fuzhuItemIsUsed(item:str):
    sql=" SELECT id FROM 分录表 WHERE 辅助=?"
    conn = config.sql_conn
    try:
        cursor = conn.cursor()
        cursor.execute(sql,[item])
        result = cursor.fetchall()
        cursor.close()
    except BaseException as e:
        msgbox("提示",str(e))
        return -1
    return len(result)  
#辅助类型是否在用
def fuzhuTypeIsUsed(type:str):
    sql=" SELECT id FROM 辅助项目表 WHERE 类别=?"
    conn = config.sql_conn
    try:
        cursor = conn.cursor()
        cursor.execute(sql,[type])
        result = cursor.fetchall()
        cursor.close()
    except BaseException as e:
        msgbox("提示",str(e))
        return -1
    return len(result)  
#获取所有辅助类型
def getFuZhuType():
    conn = config.sql_conn
    try:
        cursor = conn.cursor()
        sql = "SELECT 辅助类 FROM 辅助类别表"
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
    except BaseException as e:
        QMessageBox.warning(None,"提示",str(e),QMessageBox.Ok)
        return None
    return result

#获取辅助类下有哪些辅助项
def getFuzhuItem(fzl:str):
    '''获取辅助类下有哪些辅助项
    '''
    conn = config.sql_conn
    try:
        cursor = conn.cursor()
        sql = "SELECT 辅助 FROM 辅助项目表 WHERE 类别=?"
        cursor.execute(sql,[fzl])
        result = cursor.fetchall()
        cursor.close()
    except BaseException as e:
        QMessageBox.warning(None,"提示",str(e),QMessageBox.Ok)
        return None

    return result
#取此科目挂了那些辅助类
def getFuzhuKind(code:str):
    '''取此科目挂了那些辅助类
    '''
    conn = config.sql_conn
    try:
        cursor = conn.cursor()
        sql = "SELECT 辅助 FROM 科目表 WHERE 代码=?"
        cursor.execute(sql,[code])
        result = cursor.fetchall()
        cursor.close()
    except BaseException as e:
        QMessageBox.warning(None,"提示",str(e),QMessageBox.Ok)
    if len(result) == 1:
        fz1 = result[0][0]
        if fz1 == "":
            fz1 = None
        return fz1  
    else:
        return None

def codeToName(code:str)->str:
    '''从科目代码取科目名，不存在返回None 
    '''
    conn = config.sql_conn
    try:
        cursor = conn.cursor()
        sql = "SELECT 名称 FROM 科目表 WHERE 代码=?"
        cursor.execute(sql,[code])
        result = cursor.fetchall()
        cursor.close()
    except BaseException as e:
        QMessageBox.warning(None,"提示",str(e),QMessageBox.Ok)
    if len(result) == 1:
        return result[0][0]
    else:
        return None
    
def treeAddChildKeMu(root,type,puuid):
    try:
        cursor = config.sql_conn.cursor()
        sql1 = "SELECT uuid,名称,代码,类别,有子级,辅助 FROM 科目表 WHERE 类别=? AND 父uuid=? ORDER BY 代码"
        cursor.execute(sql1,[type,puuid])
        rows = cursor.fetchall()
        cursor.close()
    except BaseException as e:
        QMessageBox.warning(None,"提示",str(e),QMessageBox.Ok)
        return
    for row in rows:
        item=QTreeWidgetItem()
        item.setText(0,row[1])
        item.setText(1,row[2])
        item.setData(0,Qt.UserRole,row)
        root.addChild(item)
        treeAddChildKeMu(item,row[3],row[0])

def initKeMuTreeWidget(tree:QTreeWidget):
    self = tree
    tree.clear()
    tree.setColumnCount(2)
    tree.setHeaderLabels(['科目列表','科目代码'])
    tree.setColumnWidth(0,240)
    conn = config.sql_conn
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 名称 FROM 会计要素表 ORDER BY id")
        res = cursor.fetchall()
        cursor.close()
    except BaseException as e:
        QMessageBox.warning(self,"提示",str(e),QMessageBox.Ok)
        return
    for row in res:
        root=QTreeWidgetItem(tree)
        root.setText(0,row[0])
        data=["","","",row[0],1,""]
        root.setData(0,Qt.UserRole,data)
        treeAddChildKeMu(root,row[0],"")
    tree.expandAll()



class IntOnlyDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(IntOnlyDelegate, self).__init__(parent)
 
    def createEditor(self, QWidget, QStyleOptionViewItem, QModelIndex):
        editor = QLineEdit(QWidget)
        editor.setValidator(QtGui.QIntValidator())
        return editor
 
    def setEditorData(self, lineEdit, QModelIndex):
        text = QModelIndex.model().data(QModelIndex, Qt.EditRole)
        lineEdit.setText(text)
 
    def updateEditorGeometry(self, QWidget, QStyleOptionViewItem, QModelIndex):
        QWidget.setGeometry(QStyleOptionViewItem.rect)
 
    def setModelData(self, lineEditor, QAbstractItemModel, QModelIndex):
        text = lineEditor.text()
        QAbstractItemModel.setData(QModelIndex, text, Qt.EditRole)



