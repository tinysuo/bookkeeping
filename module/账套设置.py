import sys, os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import hashlib
import uuid
import config
import json
import sqlite3
import utils
import newKeMuDlg
import dbfunc

def deleteKeMu_uuid(uuid:str):
    #检测科目是还在用，在用科目不能删除
    sql = "SELECT id FROM 分录表 WHERE 科目uuid=?"
    #检测是还有下级格式
    sql1 = "SELECT id FROM 科目表 WHERE 父uuid=?"

    sql2 = "DELETE FROM 科目表 WHERE uuid=?"
    cursor = config.sql_conn.cursor()
    try:
        cursor.execute(sql,[uuid])
        if len(cursor.fetchall()) > 0:
            utils.msgbox("提示","科目已使用，不能删除在用科目")
            return
        cursor.execute(sql1,[uuid])
        if len(cursor.fetchall()) > 0:
            utils.msgbox("提示","有下级科目的科目不能删除，不能删除在用科目")
            return
        cursor.execute(sql2,[uuid])     
    except BaseException as e:
        utils.msgbox("提示",str(e))
        return   
    cursor.close() 
    config.sql_conn.commit() 
    return 0

def KeMuIsUsed(uuid):
    sql=""


class NewDurationDlg(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.modify = 0
        self.id = 0
        self.vLayout = QVBoxLayout(self)
        self.setLayout(self.vLayout)
        self.formLayout = QFormLayout()
        self.hLayout = QHBoxLayout()
        self.vLayout.addLayout(self.formLayout)
        self.hLayout.addStretch(1)
        btn_ok = QPushButton("确定")
        btn_esc = QPushButton("取消")
        btn_ok.clicked.connect(self.onBtnOkClicked)
        btn_esc.clicked.connect(self.onBtnEscClicked)
        self.hLayout.addWidget(btn_ok)
        self.hLayout.addWidget(btn_esc)
        self.hLayout.addStretch(1)
        self.vLayout.addLayout(self.hLayout)

        self.nameEdit = QLineEdit("新会计期间")
        self.Date1Edit = QDateEdit()
        self.Date2Edit = QDateEdit()
        self.Date2Edit.setDate(QDate(2099,12,31))
        self.formLayout.addRow("期间名称：",self.nameEdit)
        self.formLayout.addRow("开始时间：",self.Date1Edit)
        self.formLayout.addRow("结束时间：",self.Date2Edit)

    def setDate1(self,date_s):
        self.Date1Edit.setDate(date_s)
    def setDate2(self,date_e):
        self.Date2Edit.setDate(date_e)
    def setName(self,name):
        self.nameEdit.setText(name)
    
    def onBtnOkClicked(self):
        name = self.nameEdit.text()
        dt1 = self.Date1Edit.date().toString("yyyy-MM-dd")
        dt2 = self.Date2Edit.date().toString("yyyy-MM-dd")
        conn = config.sql_conn
        cursor = conn.cursor()        
        if self.modify == 0:
            sql = "INSERT INTO 会计期间表 (名称,开始,结束) VALUES(?,?,?)"
            try:
                cursor.execute(sql,[name,dt1,dt2])
                cursor.close()
                conn.commit()
            except BaseException as e:
                utils.msgbox("提示",str(e))    
                return 0
        elif self.modify == 1:
            sql = "UPDATE 会计期间表  SET 名称=?,开始=?,结束=? WHERE id=?"
            try:
                cursor.execute(sql,[name,dt1,dt2,self.id])
                cursor.close()
                conn.commit()
            except BaseException as e:
                utils.msgbox("提示",str(e))    
                return 0

        self.accept()

    def onBtnEscClicked(self):
       self.reject()

#新辅助项对话框
class NewFuzhuDlg(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vLayout = QVBoxLayout(self)
        self.setLayout(self.vLayout)
        self.formLayout = QFormLayout()
        self.hLayout = QHBoxLayout()
        self.vLayout.addLayout(self.formLayout)
        self.hLayout.addStretch(1)
        btn_ok = QPushButton("确定")
        btn_esc = QPushButton("取消")
        btn_ok.clicked.connect(self.onBtnOkClicked)
        btn_esc.clicked.connect(self.onBtnEscClicked)
        self.hLayout.addWidget(btn_ok)
        self.hLayout.addWidget(btn_esc)
        self.hLayout.addStretch(1)
        self.vLayout.addLayout(self.hLayout)

        self.typeLable = QLabel()
        self.itemEdit = QLineEdit()
        self.descEdit = QLineEdit()
        self.formLayout.addRow("辅助类别：",self.typeLable)
        self.formLayout.addRow("辅助项：",self.itemEdit)
        self.formLayout.addRow("描述：",self.descEdit)

    def setType(self,type):
        self.typeLable.setText(type)
    
    def onBtnOkClicked(self):
        type = self.typeLable.text()
        item = self.itemEdit.text()
        desc = self.descEdit.text()
        if type == "" or item == "":
            utils.msgbox("提示","类型和辅助项不能为空")
            return
        utils.newFuzhuItem(type,item,desc)
        self.accept()

    def onBtnEscClicked(self):
       self.reject()
#新辅助类别对话框
class NewFuzhuTypeDlg(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vLayout = QVBoxLayout(self)
        self.setLayout(self.vLayout)
        self.formLayout = QFormLayout()
        self.hLayout = QHBoxLayout()
        self.vLayout.addLayout(self.formLayout)
        self.hLayout.addStretch(1)
        btn_ok = QPushButton("确定")
        btn_esc = QPushButton("取消")
        btn_ok.clicked.connect(self.onBtnOkClicked)
        btn_esc.clicked.connect(self.onBtnEscClicked)
        self.hLayout.addWidget(btn_ok)
        self.hLayout.addWidget(btn_esc)
        self.hLayout.addStretch(1)
        self.vLayout.addLayout(self.hLayout)

        self.typeEdit = QLineEdit()
        self.descEdit = QLineEdit()
        self.formLayout.addRow("辅助类别：",self.typeEdit)
        self.formLayout.addRow("类别描述：",self.descEdit)
    
    def onBtnOkClicked(self):
        type = self.typeEdit.text()
        desc = self.descEdit.text()
        if type == "":
            utils.msgbox("提示","类别不能为空")
            return
        utils.newFuzhuType(type,desc)
        self.accept()
    def onBtnEscClicked(self):
       self.reject()
#密码修入对话框
class PassWordDlg(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vLayout = QVBoxLayout(self)
        self.setLayout(self.vLayout)
        self.formLayout = QFormLayout()
        self.hLayout = QHBoxLayout()
        self.vLayout.addLayout(self.formLayout)
        self.hLayout.addStretch(1)
        btn_ok = QPushButton("确定")
        btn_esc = QPushButton("取消")
        btn_ok.clicked.connect(self.onBtnOkClicked)
        btn_esc.clicked.connect(self.onBtnEscClicked)
        self.hLayout.addWidget(btn_ok)
        self.hLayout.addWidget(btn_esc)
        self.hLayout.addStretch(1)
        self.vLayout.addLayout(self.hLayout)

        self.oldEdit = QLineEdit()
        self.new1Edit = QLineEdit()
        self.new2Edit = QLineEdit()
        self.formLayout.addRow("旧密码：",self.oldEdit)
        self.formLayout.addRow("新密码：",self.new1Edit)
        self.formLayout.addRow("密码确认：",self.new2Edit)

    def onBtnOkClicked(self):
        oldpwd = self.oldEdit.text()
        pwdold = ("ant account" + oldpwd).encode('utf-8')
        sh256old = hashlib.sha256(pwdold).hexdigest()

        passwd1 = self.new1Edit.text()
        passwd2 = self.new2Edit.text()
        if passwd1 != passwd2:
            utils.msgbox("提示","两次密码输入不同，请重新输入")
            return
        
        pwd2 = ("ant account" + passwd1).encode('utf-8')
        sh256 = hashlib.sha256(pwd2).hexdigest()
        db_file = config.app_home+"/账套/"+config.db_name+".db"
        try:
            conn = sqlite3.connect(db_file)
            conn.executescript("PRAGMA key='%s'"%(sh256old))
            conn.executescript("PRAGMA rekey='%s'"%(sh256))
            cursor = conn.cursor()
            cursor.execute("SELECT col FROM test")
            val = cursor.fetchone()
            cursor.close()
        except BaseException as e:
            utils.msgbox("提示","密码设置失败"+str(e))
            return -1
        if val[0] == "ant":
            config.sql_conn.close()
            config.sql_conn = conn
            self.accept()
            return 0
        else:
            utils.msgbox("提示","密码设置出错")
            return -1
            

    def onBtnEscClicked(self):
       self.reject()



class AccountSeting(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.hLayout = QHBoxLayout(self)  # 设置横向布局
        self.hLayout.setContentsMargins(20,20,20,20)
        self.hLayout.setSpacing(30)
        
        self.leftLayout = QVBoxLayout()
        self.leftLayout.setSpacing(5)
        self.centLayout = QVBoxLayout()
        self.centLayout.setSpacing(5)
        self.rightLayout = QVBoxLayout()
        self.rightLayout.setSpacing(5)
        self.hLayout.addLayout(self.leftLayout)
        self.hLayout.addLayout(self.centLayout)
        self.hLayout.addLayout(self.rightLayout)
        self.hLayout.setStretch(0,1)
        self.hLayout.setStretch(1,1)
        self.hLayout.setStretch(2,1)

        lefttopLayout = QHBoxLayout()
        lefttopLayout.addWidget(QLabel("账套管理:"))
        lefttopLayout.addStretch(1)
        girdLayout = QGridLayout()
        self.passwordBtn = QPushButton("修改账套密码")
        self.saveParamBtn = QPushButton("保存账套参数")
        self.saveParamBtn.clicked.connect(self.onSaveParamClicked)
        self.passwordBtn.clicked.connect(self.onSetPasswordBtnClicked)
        girdLayout.addWidget(self.passwordBtn,0,0)
        girdLayout.addWidget(self.saveParamBtn,0,1)


        self.leftLayout.addLayout(lefttopLayout)
        self.leftLayout.addLayout(girdLayout)

        self.formLayout = QFormLayout()
        self.leftLayout.addLayout(self.formLayout)
        self.initFormLayout()
        #self.leftLayout.addStretch(1)

        left2 = QHBoxLayout()
        left2.setContentsMargins(5,40,5,5)
        left2.addWidget(QLabel("会计期间管理："))
        left2.addStretch(1)
        newDurationBtn = QPushButton("新建")
        modifyDurationBtn = QPushButton("修改")
        delDurationBtn = QPushButton("删除")
        newDurationBtn.clicked.connect(self.onNewDuration)
        modifyDurationBtn.clicked.connect(self.onModifyDuration)
        delDurationBtn.clicked.connect(self.onDelDuration)
        left2.addWidget(newDurationBtn)
        left2.addWidget(modifyDurationBtn)
        left2.addWidget(delDurationBtn)
        self.leftLayout.addLayout(left2)
        self.durationTable = QTableWidget()
        self.leftLayout.addWidget(self.durationTable)

        self.kemuTreeWidget = QTreeWidget()
        self.kemuTreeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.kemuTreeWidget.customContextMenuRequested.connect(self.createKeMuRightMenu)  # 连接到菜单显示函数
        utils.initKeMuTreeWidget(self.kemuTreeWidget)
        top2Layout = QHBoxLayout()
        top2Layout.addWidget(QLabel("科目管理："))
        


        self.centLayout.addLayout(top2Layout)
        self.centLayout.addWidget(self.kemuTreeWidget)
        
        righttopLayout = QHBoxLayout()
        righttopLayout.addWidget(QLabel("辅助核算管理："))
        righttopLayout.addStretch(1)

        self.rightLayout.addLayout(righttopLayout)

        self.fuzhuTreeWidget = QTreeWidget()
        self.fuzhuTreeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.fuzhuTreeWidget.customContextMenuRequested.connect(self.createFuZhuRightMenu)
        self.rightLayout.addWidget(self.fuzhuTreeWidget)
        self.initFuZhuTree()
        self.initDurationTalbe()
        self.showDurationTable()

    def initFuZhuTree(self):
        tree = self.fuzhuTreeWidget
        tree.clear()
        tree.setColumnCount(1)
        tree.setHeaderLabels(['辅助核算'])
        typeList = utils.getFuZhuType()
        for type in typeList:
            root=QTreeWidgetItem(tree)
            root.setText(0,type[0])
            root.setData(0,Qt.UserRole,0)
            items = utils.getFuzhuItem(type[0])
            for item in items:
                child=QTreeWidgetItem()
                child.setText(0,item[0])
                child.setData(0,Qt.UserRole,1)
                root.addChild(child)

    def initFormLayout(self):
        self.accNameEdit = QLineEdit()
        self.accNameEdit.setText(config.db_name)
        self.formLayout.addRow("账套名称:",self.accNameEdit)
        self.会计准则 = QLineEdit()
        self.会计准则.setText(dbfunc.getbookParam("会计准则"))
        self.会计准则.setDisabled(True)
        self.formLayout.addRow("会计准则:",self.会计准则)
        self.durationEdit = QLineEdit()
        self.durationEdit.setText(dbfunc.getbookParam("会计期间"))
        self.durationEdit.setDisabled(True)
        self.formLayout.addRow("会计期间:",self.durationEdit)
        self.codePlanEdit = QLineEdit()
        self.codePlanEdit.setText(dbfunc.getbookParam("编码方案"))
        self.codePlanEdit.setDisabled(True)
        self.formLayout.addRow("编码方案:",self.codePlanEdit)

        self.compnayEdit = QLineEdit()
        self.compnayEdit.setText(dbfunc.getbookParam("单位名称"))
        self.formLayout.addRow("单位名称:",self.compnayEdit)

        self.财务主管Edit = QLineEdit()
        self.财务主管Edit.setText(dbfunc.getbookParam("财务主管"))
        self.formLayout.addRow("财务主管:",self.财务主管Edit)

        self.会计Edit = QLineEdit()
        self.会计Edit.setText(dbfunc.getbookParam("会计"))
        self.formLayout.addRow("会计:",self.会计Edit)

        self.出纳Edit = QLineEdit()
        self.出纳Edit.setText(dbfunc.getbookParam("出纳"))
        self.formLayout.addRow("出纳:",self.出纳Edit)

    def onSaveParamClicked(self):
        #修改保存当前账套
        name = self.accNameEdit.text()
        if name != config.db_name:
            config.sql_conn.close()
            oldfile = config.app_home+"/账套/"+config.db_name+".db"
            newfile = config.app_home+"/账套/"+name+".db"
            os.rename(oldfile,newfile)
            config.sql_conn = None
            utils.msgbox("提示","修改账套名称需要关闭软件重新运行")

        conn = config.sql_conn
        dbfunc.setBookParam(conn,"单位名称",self.compnayEdit.text())      
        dbfunc.setBookParam(conn,"财务主管",self.财务主管Edit.text())
        dbfunc.setBookParam(conn,"会计",self.会计Edit.text())
        dbfunc.setBookParam(conn,"出纳",self.出纳Edit.text())
        conn.commit()

    def createFuZhuRightMenu(self):
        item = self.fuzhuTreeWidget.currentItem()
        leave = 0
        if item != None:
            leave = item.data(0,Qt.UserRole)
        right_menu = QMenu(self)
        actionNewType = QAction('新建辅助类别',self)
        right_menu.addAction(actionNewType)#        
        actionNewType.triggered.connect(self.onNewFuzhuTypeAction)
        if item != None and leave == 0:
            actionDelType = QAction('删除辅助类别',self)
            right_menu.addAction(actionDelType)#        
            actionDelType.triggered.connect(self.onDelFuzhuTypeAction)

            actionNewFuzhu = QAction('新建辅助项',self)
            right_menu.addAction(actionNewFuzhu)#        
            actionNewFuzhu.triggered.connect(self.onNewFuzhuAction)

        if item != None and leave == 1:
            actionDel = QAction('删除辅助项',self)
            right_menu.addAction(actionDel)#
            actionDel.triggered.connect(self.onDelFuzhuItemAction)



        right_menu.popup(QCursor.pos())

    def initDurationTalbe(self):
        self.durationTable.setColumnCount(3)
        self.durationTable.setRowCount(0)
        self.durationTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.durationTable.setSelectionBehavior(QAbstractItemView.SelectRows)        
        self.durationTable.verticalHeader().setVisible(False)   
        self.durationTable.setHorizontalHeaderLabels(["会计期间名称","开始日期","结束日期"])
        self.durationTable.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        self.durationTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.durationTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.durationTable.setColumnWidth(1,120)
        self.durationTable.setColumnWidth(2,120)
        #self.durationTable.itemDoubleClicked.connect(self.showFujian)
    def showDurationTable(self):
        rows = dbfunc.getDurations()
        line = 0
        for row in rows:
            self.durationTable.setRowCount(line+1)
            item1 = QTableWidgetItem(str(row[1]))
            item1.setData(Qt.UserRole,row[0])
            #item1.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.durationTable.setItem(line,0,item1)#摘要和UUID做为数据
            self.durationTable.setItem(line,1,QTableWidgetItem(str(row[2])))
            self.durationTable.setItem(line,2,QTableWidgetItem(str(row[3])))
            line += 1

    def onDelFuzhuTypeAction(self):
        item = self.fuzhuTreeWidget.currentItem()
        type = item.text(0)
        utils.delFuzhuType(type)
        self.initFuZhuTree() 

    def onDelFuzhuItemAction(self):
        item = self.fuzhuTreeWidget.currentItem()
        name = item.text(0)
        utils.delFuzhuItem(name)
        self.initFuZhuTree()

    def onNewFuzhuAction(self):
        item = self.fuzhuTreeWidget.currentItem()
        dlg = NewFuzhuDlg()
        dlg.setType(item.text(0))
        dlg.exec()
        self.initFuZhuTree()

    def onNewFuzhuTypeAction(self):
        dlg = NewFuzhuTypeDlg(self)
        dlg.exec()
        self.initFuZhuTree()

    def createKeMuRightMenu(self):
        item = self.kemuTreeWidget.currentItem()     
        if item == None:
            return 
        KeMu = item.data(0,Qt.UserRole)

        self.right_menu = QMenu(self)
        actionNew = QAction('新建科目',self)
        self.right_menu.addAction(actionNew)#
        actionNew.triggered.connect(self.onNewKemuAction)

        if KeMu[0] != "":
            actionModify = QAction('编辑科目',self)
            self.right_menu.addAction(actionModify)#
            actionModify.triggered.connect(self.onModifyKemuAction)

            actionDel = QAction('删除科目',self)
            self.right_menu.addAction(actionDel)#
            actionDel.triggered.connect(self.onDelKemuAction)

        self.right_menu.popup(QCursor.pos())

    def onNewKemuAction(self):
        item = self.kemuTreeWidget.currentItem()
        if item == None:
            return 
        KeMu = item.data(0,Qt.UserRole)
        if KeMu == None:
            return
        try:
            dlg = newKeMuDlg.newKeMuDlg(self)
            dlg.uuid = str(uuid.uuid1())
            dlg.type = KeMu[3]
            dlg.puuid = KeMu[0]
            dlg.pname = KeMu[1]
            dlg.initData()
            dlg.exec()
        except BaseException as e:
            utils.msgbox("提示",str(e))
            return
        self.kemuTreeWidget.clear()
        utils.initKeMuTreeWidget(self.kemuTreeWidget) 

    def onDelKemuAction(self):
        item = self.kemuTreeWidget.currentItem()
        if item == None:
            return 
        kumu = item.data(0,Qt.UserRole)
        if kumu == None:
            return
        ret = deleteKeMu_uuid(kumu[0])
        if ret == 0:
            self.kemuTreeWidget.clear()
            utils.initKeMuTreeWidget(self.kemuTreeWidget)

    def onModifyKemuAction(self):
        item = self.kemuTreeWidget.currentItem()
        if item == None:
            return 
        kemu = item.data(0,Qt.UserRole)
        if kemu == None:
            return
        try:
            dlg = newKeMuDlg.newKeMuDlg(self)
            dlg.uuid = kemu[0]
            dlg.code = kemu[2]
            dlg.name = kemu[1]
            dlg.type = kemu[3]
            dlg.modify = 1
            dlg.initData()
            dlg.exec()
        except BaseException as e:
            utils.msgbox("提示",str(e))
            return
        self.kemuTreeWidget.clear()
        utils.initKeMuTreeWidget(self.kemuTreeWidget)

    def onSetPasswordBtnClicked(self):
        dlg = PassWordDlg(self)
        dlg.exec()

    def onNewDuration(self):
        #决定是自然月还是自由期间
        durationType = dbfunc.getbookParam("会计期间")
        if durationType == "自然月":
            utils.msgbox("提示","自然月会计期间不能新建期间，请新建下一年账套")
            return
        last_duration = dbfunc.getLastDuration()

        dlg = NewDurationDlg(self)      
        date_s = QDate().fromString(last_duration[3],"yyyy-M-d")
        date_s = date_s.addDays(1)
        dlg.setDate1(date_s)
        dlg.exec()
        self.showDurationTable()
     
    def onModifyDuration(self):
        durationType = dbfunc.getbookParam("会计期间")
        if durationType == "自然月":
            utils.msgbox("提示","自然月会计期间不能修改")
            return
        #找出最新会计期间
        last_duration = dbfunc.getLastDuration()
        #修改
        dlg = NewDurationDlg(self) 
        dlg.modify = 1  
        dlg.id = last_duration[0]  
        dlg.setName(last_duration[1]) 
        date_s = QDate().fromString(last_duration[2],"yyyy-M-d")
        dlg.setDate1(date_s)
        date_e = QDate().fromString(last_duration[3],"yyyy-M-d")
        dlg.setDate2(date_e)
        dlg.exec()

        self.showDurationTable()
        
    def onDelDuration(self):
        durationType = dbfunc.getbookParam("会计期间")
        if durationType == "自然月":
            utils.msgbox("提示","自然月会计期间不能删除")
            return
        #找出最新会计期间
        last_duration = dbfunc.getLastDuration()
        #确定期间内有没有分录
        lines = dbfunc.durationIsUsed(last_duration)
        if lines >0:
            utils.msgbox("提示","已使用会计期间不能删除")
            return
        #如果没有用可以删除
        dbfunc.delDuration(last_duration[0])

        self.showDurationTable()