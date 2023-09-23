import sys, os
import uuid
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *
import tempfile
import hashlib
import config
import json
import sqlite3
import utils
import KeMuDialog
import printer

from dbfunc import *
import shellexecute
import openpyxl


class voucheWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.isNewPZ = 1 #是否是新凭证，新凭证直接insert 修改要updata
        self.currentPZ_uuid = 0 #正在修改凭证的ID
        self.modifyed = 0
        self.isnew = 1
        self.hLayout = QHBoxLayout(self)  # 设置横向布局
        self.hLayout.setContentsMargins(15,15,15,15)
        self.hLayout.setSpacing(30)
        
        self.leftLayout = QVBoxLayout()
        self.rightLayout = QVBoxLayout()
        self.leftLayout.setSpacing(5)
        self.rightLayout.setSpacing(5)
        self.hLayout.addLayout(self.leftLayout)
        self.hLayout.addLayout(self.rightLayout)
        self.hLayout.setStretch(0,1)
        self.hLayout.setStretch(1,2)
        
        btns1 = []
        btns1.append(QPushButton("上张"))
        btns1.append(QPushButton("下张"))
        btns1.append(QPushButton("新单"))

        leftLayout0 = QHBoxLayout() #左则顶部layout        
        for btn in btns1:
            leftLayout0.addWidget(btn)
            btn.clicked.connect(lambda :self.comandbtnsClicked(btn))

        self.leftLayout.addLayout(leftLayout0)

        leftLayout1 = QHBoxLayout() #左则顶部layout
        label1 = QLabel("会计期间:")
        self.KaiJiQiJian = QLabel("")
        label1.setFixedHeight(48)        
        duration = getDuration(config.kj_date.toString("yyyy-MM-dd"))
        if duration != None:
            self.KaiJiQiJian.setText("%s(%s 至 %s)"
                %(duration[1],duration[2],duration[3]))
        leftLayout1.addWidget(label1)
        leftLayout1.addWidget(self.KaiJiQiJian)
        leftLayout1.addStretch(1)

        self.leftLayout.addLayout(leftLayout1)
        #凭证表
        self.pzTable = QTableWidget()
        self.pzTable.setColumnCount(5)
        self.pzTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.pzTable.verticalHeader().setVisible(False)
        self.pzTable.setSelectionBehavior(QAbstractItemView.SelectRows) 
        self.pzTable.setHorizontalHeaderLabels(["凭证号","日期","凭证摘要","附件","记账"])
        self.pzTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.pzTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.pzTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.pzTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.pzTable.horizontalHeader().setSectionResizeMode(3, QHeaderView.Interactive)
        self.pzTable.horizontalHeader().setSectionResizeMode(4, QHeaderView.Interactive)
        self.pzTable.setColumnWidth(0, 60) 
        self.pzTable.setColumnWidth(1, 120)  
        self.pzTable.setColumnWidth(3, 40) 
        self.pzTable.setColumnWidth(4, 40)           
        self.pzTable.itemSelectionChanged.connect(self.tableitemSelectionChanged)
        self.pzTable.itemDoubleClicked.connect(self.tableitemSelectionChanged)

        self.leftLayout.addWidget(self.pzTable)
        #self.leftLayout.addStretch(1)

        self.layoutRight1 = QHBoxLayout()   #右则第一行按钮布局
        self.layoutRight2 = QHBoxLayout()   #右则第二行按钮布局
        self.rightLayout.addLayout(self.layoutRight1)
        self.rightLayout.addLayout(self.layoutRight2)
        
        btns = []
        # btns.append(QPushButton("新单"))
        self.saveBtn= QPushButton("保存")
        btns.append(self.saveBtn)
        btns.append(QPushButton("记账"))
        btns.append(QPushButton("反记账"))
        btns.append(QPushButton("预览"))
        btns.append(QPushButton("打印"))
        # btns.append(QPushButton("上张"))
        # btns.append(QPushButton("下张"))
        btns.append(QPushButton("添加分录"))
        btns.append(QPushButton("删除分录"))
        for btn in btns:
            self.layoutRight1.addWidget(btn)
            btn.clicked.connect(lambda :self.comandbtnsClicked(btn))

        self.pzNo = QLabel()
        self.pzNo.setFixedHeight(48)
        self.pzDate = QDateEdit()
        self.pzDesc = QLineEdit()
        self.pzFuJan = QLineEdit()
        self.pzFuJan.setMaximumWidth(40)
        self.pzDesc.setMinimumWidth(300)
        self.pzDesc.textChanged.connect(self.FL_itemChanged)
        self.pzFuJan.textChanged.connect(self.FL_itemChanged)
        self.pzDate.dateChanged.connect(self.FL_itemChanged)
        self.layoutRight2.addWidget(QLabel("凭证号:"))
        self.layoutRight2.addWidget(self.pzNo)
        self.layoutRight2.addStretch(1)
        self.layoutRight2.addWidget(QLabel("凭证摘要:"))
        self.layoutRight2.addWidget(self.pzDesc)
        self.layoutRight2.addStretch(1)
        self.layoutRight2.addWidget(QLabel("日期:"))
        self.layoutRight2.addWidget(self.pzDate)

        self.layoutRight2.addStretch(1)
        self.layoutRight2.addWidget(QLabel("附件数:"))
        self.layoutRight2.addWidget(self.pzFuJan)

        #分录表
        self.flLayout = QVBoxLayout()
        self.rightLayout.addLayout(self.flLayout)
        self.initFenluTable()

        self.layoutRight4 = QHBoxLayout()   #右则表格下方布局
        self.layoutRight5 = QHBoxLayout()   #右则表格下方布局2        
        self.rightLayout.addLayout(self.layoutRight4)
        self.rightLayout.addLayout(self.layoutRight5)

        self.initFujianTable()

        self.rightLayout.setStretch(2,4)
        self.rightLayout.setStretch(4,3)
        self.setAcceptDrops(True)  
        self.newPingzheng()
        self.showPZ_Table()
    #初始化分录表
    def initFenluTable(self):
        self.flLayout.setSpacing(0)
        self.flTable = QTableWidget()
        self.flTable.setColumnCount(4)
        self.flTable.setRowCount(2)
        lineheight = self.flTable.rowHeight(0)
        self.flTable.setFixedHeight(lineheight*10)        
        self.flTable.verticalHeader().setVisible(False)   
        self.flTable.setHorizontalHeaderLabels(["摘要","科目","借方金额","贷方金额"])
        self.flTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.flTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)
        self.flTable.horizontalHeader().setSectionResizeMode(3, QHeaderView.Interactive)
        self.flTable.setColumnWidth(2,120)
        self.flTable.setColumnWidth(3,120)
        #self.flTable.setItemDelegateForColumn(1, utils.IntOnlyDelegate(self))      
        #self.flTable.setItemDelegateForColumn(2, utils.DoubleOnlyDelegate(self))
        #self.flTable.setItemDelegateForColumn(3, utils.DoubleOnlyDelegate(self))
        self.flTable.itemChanged.connect(self.FL_itemChanged)
        self.flTable.cellChanged.connect(self.flCellChanged)
        self.flTable.cellDoubleClicked.connect(self.flCellDoubleClicked)
        self.flLayout.addWidget(self.flTable)

        self.heJiTable = QTableWidget()
        self.heJiTable.setColumnCount(4)
        self.heJiTable.setRowCount(1)
        self.heJiTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.heJiTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)
        self.heJiTable.horizontalHeader().setSectionResizeMode(3, QHeaderView.Interactive)
        self.heJiTable.setColumnWidth(2,120)
        self.heJiTable.setColumnWidth(3,120)
        self.heJiTable.horizontalHeader().setVisible(False)
        self.heJiTable.verticalHeader().setVisible(False)
        self.heJiTable.setFixedHeight(40)
        self.heJiTable.setRowHeight(0,40)
        self.heJiTable.setSpan(0,0,1,2)
        self.heJiTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.heJiTable.setObjectName("hejiTalbe")
        self.heJiTable.setItem(0,0,QTableWidgetItem("合计："))
        self.heJiTable.item(0,0).setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.heJiTable.setItem(0,2,QTableWidgetItem("￥%.2f"%(0.0)))
        self.heJiTable.setItem(0,3,QTableWidgetItem("￥%.2f"%(0.0)))
        self.heJiTable.item(0,2).setTextAlignment(Qt.AlignRight| Qt.AlignVCenter )
        self.heJiTable.item(0,3).setTextAlignment(Qt.AlignRight| Qt.AlignVCenter )

        self.flLayout.addWidget(self.heJiTable)
    #初始化电子附件表
    def initFujianTable(self):
        self.layoutRight4.addWidget(QLabel("电子附件表："))
        self.layoutRight4.addStretch(1)
        btns2 = []
        btns2.append(QPushButton("添加附件"))
        btns2.append(QPushButton("删除附件"))
        btns2.append(QPushButton("打开附件"))
        for btn in btns2:
            self.layoutRight4.addWidget(btn)
            btn.clicked.connect(lambda :self.comandbtnsClicked(btn))
            btn.setMinimumWidth(120)
            #btn.setStyleSheet("padding-left:20px;padding-right:20px")

        self.fujianTable = QTableWidget()
        self.layoutRight5.addWidget(self.fujianTable)
        self.fujianTable.setColumnCount(3)
        self.fujianTable.setRowCount(0)
        self.fujianTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.fujianTable.setSelectionBehavior(QAbstractItemView.SelectRows)        
        self.fujianTable.verticalHeader().setVisible(False)   
        self.fujianTable.setHorizontalHeaderLabels(["序号","格式","文件名"])
        self.fujianTable.horizontalHeader().setSectionResizeMode(0,QHeaderView.Fixed)
        self.fujianTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.fujianTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.fujianTable.setColumnWidth(0,80)
        self.fujianTable.setColumnWidth(1,80)
        self.fujianTable.itemDoubleClicked.connect(self.showFujian)

    def dragEnterEvent(self, e):
        if e.mimeData().hasText():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        filePathList = e.mimeData().text()
       
        files = filePathList.split('\n') #拖拽多文件
        print(files)
        for file in files:
            if file=="":
                break
            file = file.replace('file:///', '', 1) #去除文件地址前缀的特定字符
            saveFujianFile(self.currentPZ_uuid,file)
        self.showFujiaTalbe()

    def addFujianClicked(self):
        if self.isnew == 1:
            msgbox("提示","未保存的新凭证不能添加电子附件")
            return
        options = QFileDialog.Options()
        file_filter = "Images (*.png *.xpm *.jpg);;All Files (*)"

        file_names, _ = QFileDialog.getOpenFileNames(self, 
                        "选择文件", "", file_filter)

        for file in file_names:
            saveFujianFile(self.currentPZ_uuid,file)
        self.showFujiaTalbe()

    def updateHejiTalbe(self):
        jie = 0
        dai = 0 
        n = self.flTable.rowCount()
        for i in  range(0,n):
            item2 = self.flTable.item(i,2)
            item3 = self.flTable.item(i,3)
            if item2 == None:
                val2 = 0
            elif item2.text()=="":
                val2 = 0
            else:
                val2 = float(item2.text())
            if item3 == None:
                val3 = 0
            elif item3.text()=="":
                val3 = 0
            else:
                val3 = float(item3.text())
            jie += val2
            dai += val3

        self.heJiTable.item(0,2).setText("￥%.2f"%jie)
        self.heJiTable.item(0,3).setText("￥%.2f"%dai)

    def showFujiaTalbe(self):
        n = self.fujianTable.rowCount()
        for i in range(n):
            self.fujianTable.removeRow(0)

        items = getFujianList(self.currentPZ_uuid)       
        n = 0
        for item in items:
            self.fujianTable.setRowCount(n+1)
            it = QTableWidgetItem(str(n))
            it.setData(Qt.UserRole,item[0])
            self.fujianTable.setItem(n,0,it)
            self.fujianTable.setItem(n,1,QTableWidgetItem(item[2]))
            self.fujianTable.setItem(n,2,QTableWidgetItem(item[1]))
            n += 1 


    def showFujian(self):
        # 如果单元格对象为空
        items = self.fujianTable.selectedItems()
        if len(items) == 0:
            return
        id = items[0].data(Qt.UserRole)
        format,data = getFujianData(id)
        if data == None:
            return
        #f = tempfile.NamedTemporaryFile(suffix=format,delete=False) #
        f = tempfile.TemporaryFile(suffix=format,delete=False) #
        f.write(data)
        shellexecute.exec("open",f.name,"",1)
        f.close()

    def removeFujian(self):
        items = self.fujianTable.selectedItems()
        if len(items) == 0:
            return
        id = items[0].data(Qt.UserRole)
        removeFujianOnDB(id)
        self.showFujiaTalbe()

    def tableitemSelectionChanged(self):
        #如果正在编辑凭证已经修改，提示
        if self.modifyed == 1 :
            dlg = QMessageBox()
            dlg.setText("当前凭证已经修改，是否需要保存")
            dlg.addButton('我要保存', QMessageBox.AcceptRole)
            dlg.addButton('不保存重新打开新凭证', QMessageBox.RejectRole)
            ret = dlg.exec()
            if ret == QMessageBox.AcceptRole:
                return
        # 如果单元格对象为空
        items = self.pzTable.selectedItems()
        if len(items) == 0:
            return
        uuid = items[0].data(Qt.UserRole)
        self.currentPZ_uuid = uuid
        self.pzNo.setText(items[0].text())
        self.pzDate.setDate(QDate().fromString(items[1].text(),"yyyy-MM-dd")) #
        self.pzDesc.setText(items[2].text())
        self.pzFuJan.setText(items[3].text())
        self.showFenLuTable(uuid)
        self.showFujiaTalbe()
        self.modifyed = 0
        self.saveBtn.setDisabled(True)
        self.isnew = 0        

    def FL_itemChanged(self):
        # 如果单元格对象为空
        self.modifyed = 1
        self.saveBtn.setDisabled(False)

    def comandbtnsClicked(self,btn):
        if self.sender().text() == "保存":        
            self.savePingZheng()
        elif self.sender().text() == "新单":
            self.newPingzheng()
        elif self.sender().text() == "添加分录":
            self.addFengLu()
        elif self.sender().text() == "删除分录":
            self.delFenglu()
        elif self.sender().text() == "上张":
            row = self.pzTable.currentRow()
            self.pzTable.selectRow(row-1)
        elif self.sender().text() == "下张":
            row = self.pzTable.currentRow()
            self.pzTable.selectRow(row+1) 
        elif self.sender().text() == "记账":
            if self.modifyed == 1:
                msgbox("提示","请先保存凭证后再记账")
                return
            record_keeping(self.currentPZ_uuid)
            self.showPZ_Table()
        elif self.sender().text() == "反记账":
            unRecodeKeeping(self.currentPZ_uuid)
            self.showPZ_Table()
        elif self.sender().text() == "打印":
            self.printPingzheng()
        elif self.sender().text() == "预览":
            self.previewPingzheng()
        elif self.sender().text() == "添加附件":
            self.addFujianClicked()  
        elif self.sender().text() == "删除附件":
            self.removeFujian()                         

    def printPingzheng(self):
        if self.modifyed == 1:
            self.msg("提示","打印凭证前先保存凭证")
            return
        myprinter = printer.MyPrinter("pz")
        myprinter.pzuuid = self.currentPZ_uuid
        myprinter.print()

    def previewPingzheng(self):
        if self.modifyed == 1:
            self.msg("提示","打印凭证前先保存凭证")
            return
        myprinter = printer.MyPrinter("pz")
        myprinter.pzuuid = self.currentPZ_uuid
        myprinter.preview(self)

    def printPingzheng1(self):
        filename = config.app_home + '\\template\\pz.xlsx'
        book = openpyxl.load_workbook(filename)
        # 获取sheet页
        sheet1  = book['Sheet1']

        uuid = self.currentPZ_uuid
        result =getFengluByPingzheng(uuid)
        if result == None:
            return
        
        line = 0
        for row in result:
            cell1 = "A%d"%(5+line)
            sheet1[cell1]=row[1]            
            kemu = getKemuCodeName(row[2])
            cell2 = "B%d"%(5+line)
            if kemu != None:
                text = "%s-%s"%(kemu[0],kemu[1])
                if row[5]!=None and row[5]!="":
                    text = text + "(%s)"%row[5]
                sheet1[cell2]=text 

            cell3 = "C%d"%(5+line)
            sheet1[cell3]=row[3]/100 
            cell4 = "D%d"%(5+line)
            sheet1[cell4]=row[4]/100 
            line = line+1
        #ws3 = wb2.get_sheet_by_name('mytest')

        tmp = tempfile.mkstemp(suffix = ".xlsx") #tempfile.TemporaryFile(suffix = ".xlsx")
        book.save(tmp[1])
        book.close()  
        #shellexecute.exec("print",filename,"",0)
        print(tmp[1])
        shellexecute.exec("open","https://www.bing.com","",0)

    def showPZ_Table(self):
        list = dbGetPingZhengList(config.kj_date.toString("yyyy-MM-dd"))
        line = 0
        for row in list:
            self.pzTable.setRowCount(line+1)
            for col in range(0,5):
                self.pzTable.setItem(line,col,QTableWidgetItem(str(row[col])))
                self.pzTable.item(line,col).setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                if col == 4:
                    if row[col] == 1:
                        self.pzTable.item(line,col).setText("√")
                    else:
                        self.pzTable.item(line,col).setText("")
            self.pzTable.item(line,0).setData(Qt.UserRole,row[5])
            line = line+1

    def showFenLuTable(self,uuid):
        result =getFengluByPingzheng(uuid)
        if result == None:
            return
        line = 0
        for row in result:
            self.flTable.setRowCount(line+1)
            item1 = QTableWidgetItem(str(row[1]))
            item1.setData(Qt.UserRole,row[0])
            #item1.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.flTable.setItem(line,0,item1)#摘要和UUID做为数据
            
            lable = getKeMuLable(row[2])

            if row[5] != "":
                lable += "(%s)"%(row[5])

            item2 = QTableWidgetItem(lable)
            item2.setData(Qt.UserRole,[row[2],row[5]])
            self.flTable.setItem(line,1,item2)

            item3= QTableWidgetItem(str(row[3]/100))
            item3.setTextAlignment(Qt.AlignRight| Qt.AlignVCenter)
            self.flTable.setItem(line,2,item3)#借方金额
            item4 = QTableWidgetItem(str(row[4]/100))
            item4.setTextAlignment(Qt.AlignRight| Qt.AlignVCenter)
            self.flTable.setItem(line,3,item4)#贷方金额
            line = line+1
        #显示凭证号 日期 分录数
    
    def getItemText(self,row:int,col:int):
        item = self.flTable.item(row,col)
        if item == None:
            return ""
        text = item.text()
        if text == None:
            return ""
        return text

    def getKemu_uuid(self,row:int,col:int):
        item = self.flTable.item(row,col)
        if item == None:
            return ""
        data = item.data(Qt.UserRole)
        if data ==None:
            return ""
        else:
            return data[0]
    def msg(self,info):
        QMessageBox.warning(self,"提示",info,QMessageBox.Ok) 
    def getFenLu_fuzhu(self,row):
        item = self.flTable.item(row,1)
        if item == None:
            return ""
        data = item.data(Qt.UserRole)
        if data ==None:
            return ""
        else:
            return data[1]
    def getPZh_info(self):
        pz_info=[]
        pz_info.append(self.currentPZ_uuid) #0 uuid
        pz_info.append(self.pzNo.text())    #1 凭证号
        pz_info.append(self.pzDate.date().toString("yyyy-MM-dd"))    #2 凭证日期
        pz_info.append(self.pzDesc.text())    #3 摘要
        pz_info.append(self.pzFuJan.text())    #4 附件数
        if pz_info[3] == "":
            QMessageBox.warning(self,"提示","凭证摘要不能为空",QMessageBox.Ok)
            return
        if pz_info[4] == "":
            QMessageBox.warning(self,"提示","附件数不能为空",QMessageBox.Ok)
            return
        return pz_info
    
    def getFL_info(self):
        try:
            flv = []
            rowCount = self.flTable.rowCount()           
            for i in range(0,rowCount,1):
                item = []
                item.append(str(uuid.uuid1()))      #0 uuid
                item.append(self.currentPZ_uuid)    #1 凭证uuid
                item.append(self.getItemText(i,0))    #2 摘要
                item.append(self.getKemu_uuid(i,1))    #3 科目uuid                
                t1 = self.getItemText(i,2)
                t2 = self.getItemText(i,3)
                if t1=="":
                    t1="0.0"
                if t2=="":
                    t2 = "0.0"
                item.append(float(t1)*100)          #4借
                item.append(float(t2)*100)          #5
                item.append(self.getFenLu_fuzhu(i))      #6辅助
                
                if item[2] == "":
                    self.msg("凭证摘要不能为空")
                    return 
                if item[3] == "":
                    self.msg("科目代码 不能为空")
                    return 
                if  item[4] != 0.0 and item[5] !=0.0:
                    self.msg("借贷金额不能同时不为零")
                    return
                if  item[4] == 0.0 and item[5] ==0.0:
                    self.msg("借贷金额不能同时为零")
                    return
                flv.append(item)

        except BaseException as e:
            self.msg(str(e))

        return flv       
    def savePingZheng(self):
        duration = getDuration(config.kj_date.toString("yyyy-MM-dd"))
        date1 = QDate.fromString(duration[2],"yyyy-MM-dd")
        date2 = QDate.fromString(duration[3],"yyyy-MM-dd")
        date0 = self.pzDate.date()
        
        if date0 < date1 or date0 > date2:
            msgbox("提示","当前凭证日期在不当前会计期间内")
            return

        pz_info = self.getPZh_info()
        if pz_info == None:
            return        
        fl_info = self.getFL_info()
        if fl_info == None:
            return
        jie = 0
        dai = 0
        for fl in fl_info:
            jie += fl[4]
            dai += fl[5]
        if jie != dai:
            utils.msgbox("出错","借贷合计金额应相等，请核对金额")
            return
        ret = dbSavePingzheng(pz_info,fl_info)
        if ret != 1:
            return
        self.isnew = 0 #保存成功就不是新的了，需要进行更新操作
        self.modifyed = 0        
        self.showPZ_Table()
        self.saveBtn.setDisabled(True)
        config.kj_date = self.pzDate.date()

    def addFengLu(self):
        n = self.flTable.rowCount()
        if n >= 32:
            QMessageBox.warning(self,"提示","单张记账凭证分录数已经达上限",QMessageBox.Ok)
            return 
        self.flTable.setRowCount(n+1)  
    def delFenglu(self):
        n = self.flTable.rowCount()
        if n <= 2:
            QMessageBox.warning(self,"提示","单张记账凭证分录数最少为2",QMessageBox.Ok)
            return 
        i = self.flTable.currentRow()
        self.flTable.removeRow(i)
        
    def flCellChanged(self,row,col):
        if row == 0 and col==0:
            if self.pzDesc.text()[0:3] == "新凭证":
                self.pzDesc.setText(self.flTable.item(row,col).text())
        if col == 1:
            item = self.flTable.item(row,col)
            text = item.text()
            if text.isdigit():
                kemu = getKumuByCode(text)
                if kemu == None:
                    self.flCellDoubleClicked(row,col)
                    return                  
                lable = getKeMuLable(kemu[0]) 
                fuzhu = ""                            
                if kemu[3] != None and kemu[3] !="": #说有挂了辅助核算
                    #self.flCellDoubleClicked(row,col)
                    #return 
                    dlg = FuzhuSelectDlg(self,kemu[0])                   
                    dlg.exec() 
                    fuzhu = dlg.fuzhu 
                if fuzhu != "":
                    lable += "(%s)"%(fuzhu)      
                item.setText(lable)
                item.setData(Qt.UserRole,[kemu[0],fuzhu])

        elif col == 2 or col == 3:
            text = self.flTable.item(row,col).text()
            if text == "":
                text = "0" 
            try:
                fv = float(text)
            except:
                fv = 0
            if fv==0:  
                self.flTable.item(row,col).setText("")
            else:
                self.flTable.item(row,col).setText("%.2f"%fv)
            self.flTable.item(row,col).setTextAlignment(Qt.AlignRight| Qt.AlignVCenter)

            self.updateHejiTalbe()

    def flCellDoubleClicked(self,row,col):
        if col == 1:
            dlg = KeMuDialog.KeMuDialog()
            item = self.flTable.item(row,col)
            if item == None:
                item = QTableWidgetItem()
                self.flTable.setItem(row,col,item)            
            if dlg.exec_() == QDialog.Accepted:                
                lable = getKeMuLable(dlg.result[0])
                fuzhu = dlg.result[1]
                if fuzhu != "":
                    lable = lable +"(%s)"%fuzhu
                item.setText(lable)
                item.setData(Qt.UserRole,dlg.result)
                item.setSelected(False)
                nrow= row
                ncol = col+1
                if col >= 3:
                    ncol = 0
                    nrow = row+1
                self.flTable.setCurrentCell(nrow,ncol)

    def initFuzhuCol(self,row:int):   
        item = self.flTable.item(row,1)
        data = item.data(Qt.UserRole)
        item2 = QTableWidgetItem()
        item2.setData(Qt.UserRole,data)
        self.flTable.setItem(row,2,item2) 
        return

    def keyPressEvent(self, event):
        if self.flTable.hasFocus():
            row = self.flTable.currentRow()
            col = self.flTable.currentColumn()
            if(event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return):
                nrow= row
                ncol = col+1
                if col >= 3:
                    ncol = 0
                    nrow = row+1
                self.flTable.setCurrentCell(nrow,ncol)
                #下一行的摘要自动填入下一个
                if ncol == 0 and nrow >= 1:
                    item0 = self.flTable.item(nrow-1,ncol)
                    if item0 != None:
                        desc = self.flTable.item(nrow-1,ncol).text()
                        item = self.flTable.item(nrow,ncol)    
                        if item == None:
                            item = QTableWidgetItem()
                            self.flTable.setItem(nrow,ncol,item)
                        if item.text() == "":
                            item.setText(desc)
            elif event.key() == Qt.Key_Delete:
                item0 = self.flTable.item(row,col)
                if item0 != None:
                     item0.setText("")

    def newPingzheng(self):
        if self.modifyed == 1:
            rebtn = QMessageBox.warning(self,"提示","确认要放弃已经编辑的凭证内容吗",
                                        QMessageBox.Yes | QMessageBox.No )
            if rebtn != QMessageBox.Yes:
                return
        max = getMaxPZ_No(config.kj_date.toString("yyyy-MM-dd"))+1
        self.pzNo.setText(str(max))
        self.pzDesc.setText("新凭证 %s"%(str(max)))
        self.pzFuJan.setText("0")
        self.flTable.setRowCount(0)
        self.flTable.setRowCount(2)
        self.saveBtn.setDisabled(True)
        self.pzDate.setDate(config.kj_date)
        self.currentPZ_uuid = str(uuid.uuid1()) 
        self.isnew = 1
        self.modifyed = 0





class FuzhuSelectDlg(QDialog):
    def __init__(self,parent,km_uuid, *args, **kwargs):
        super().__init__(parent,*args, **kwargs)       
        self.fuzhu = ""
        self.kemu_uuid = km_uuid
        self.vLayout = QVBoxLayout(self)
        self.setLayout(self.vLayout)
        self.vLayout.setContentsMargins(30,50,30,50)
        self.vLayout.setSpacing(30)
        self.formLayout = QFormLayout()
        self.formLayout.setSpacing(5)
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
        self.kemuLable = QLabel(getKeMuLable(km_uuid))
        self.fuzhuCBX = QComboBox()

        self.formLayout.addRow("",QLabel("当前科目设置了辅助核算，请选择辅助项目"))
        self.formLayout.addRow("",QLabel(""))
        self.formLayout.addRow("科目：",self.kemuLable)
        self.formLayout.addRow("辅助：",self.fuzhuCBX)
        

        fz_items = getKemuFuzhu(self.kemu_uuid)
        if fz_items[0] == 1:#没有挂辅助可以直接返回
            self.fuzhuCBX.clear()
            self.fuzhuCBX.addItem("当前分录不设置辅助","")
            for fz in fz_items[1]:
                self.fuzhuCBX.addItem(fz,fz)
    
    def onBtnOkClicked(self):
        self.fuzhu = self.fuzhuCBX.currentData(Qt.UserRole)
        self.accept()

    def onBtnEscClicked(self):
       self.reject()

