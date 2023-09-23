import sys, os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *
import config
import sqlite3
import utils
from dbfunc import *
import printer

class MSWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.currentKeMu = None
        self.hLayout = QHBoxLayout(self)  # 设置横向布局
        self.hLayout.setContentsMargins(15,15,15,15)
        self.hLayout.setSpacing(20)
        self.leftLayout = QVBoxLayout()
        self.rightLayout = QVBoxLayout()
        self.leftLayout.setSpacing(5)
        self.rightLayout.setSpacing(5)
        self.hLayout.addLayout(self.leftLayout)
        self.hLayout.addLayout(self.rightLayout)
        self.hLayout.setStretch(0,1)
        self.hLayout.setStretch(1,4)

        self.durationCbox = QComboBox()
        
        durations = getDurations()
        curdur = getDuration(config.kj_date.toString("yyyy-MM-dd"))
        for dur in durations:
             text = "%s(%s - %s)"%(dur[1],dur[2],dur[3])
             self.durationCbox.addItem(text,dur)
             if dur[0] == curdur[0]:
                 self.durationCbox.setCurrentIndex(self.durationCbox.count()-1)
        self.fuzhuCbox = QComboBox()         
        self.kemuTree= QTreeWidget()
        self.msTable=QTableWidget()
        self.leftLayout.addWidget(self.durationCbox)
        self.leftLayout.addWidget(self.kemuTree)
        #self.leftLayout.addWidget(self.fuzhuCbox)
        
        rightTopLayout = QHBoxLayout()
        self.rightLayout.addLayout(rightTopLayout)
        self.rightLayout.addWidget(self.msTable)

        self.frashBtn = QPushButton("刷新")
        self.previewBtn = QPushButton("预览")
        self.printBtn = QPushButton("打印")
        self.printAllBtn = QPushButton("打印全部")
        self.exportExcelBtn = QPushButton("导出excel")

        rightTopLayout.addWidget(self.fuzhuCbox)
        rightTopLayout.addWidget(self.frashBtn)
        rightTopLayout.addWidget(self.previewBtn)
        rightTopLayout.addWidget(self.printBtn)
        rightTopLayout.addWidget(self.printAllBtn)
        rightTopLayout.addWidget(self.exportExcelBtn)

        self.previewBtn.clicked.connect(self.onPreviewClicked)
        
        self.initMSTable(self.msTable)
        utils.initKeMuTreeWidget(self.kemuTree)

        self.frashBtn.clicked.connect(self.frashBtnClicked)

        self.kemuTree.currentItemChanged.connect(self.accountChanged)
        self.durationCbox.currentIndexChanged.connect(self.param_changed)
        self.fuzhuCbox.currentIndexChanged.connect(self.param_changed)

    def initMSTable(self,table:QTableWidget):
        table.setColumnCount(7)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QAbstractItemView.SelectRows) 
        table.setHorizontalHeaderLabels(["日期","凭证号","摘要","借方","贷方","方向","余额"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        table.setColumnWidth(0, 120) 
        table.setColumnWidth(1, 120)  
        table.setColumnWidth(3, 120) 
        table.setColumnWidth(4, 120) 
        table.setColumnWidth(5, 60) 
        table.setColumnWidth(6, 120)          
    
    def accountChanged(self):
        item = self.kemuTree.currentItem()
        if item == None:
            return
        KeMu = item.data(0,Qt.UserRole)
        if KeMu == None:
            return
        if KeMu == "":
            return
        if KeMu[0] == "":
            return
       
        self.fuzhuCbox.currentIndexChanged.disconnect()  
        self.fuzhuCbox.clear()       
        fuzhu = getKemuFuzhu(KeMu[0])
        self.fuzhuCbox.addItem("查看全部","")
        if fuzhu != None and fuzhu[1] != None:
            self.fuzhuCbox.setCurrentIndex(0)
            for fz in fuzhu[1]:
                self.fuzhuCbox.addItem(fz,fz)
        self.fuzhuCbox.currentIndexChanged.connect(self.param_changed)
        self.param_changed()
    
    def param_changed(self):
        item = self.kemuTree.currentItem()
        if item == None:
            return
        KeMu = item.data(0,Qt.UserRole)
        self.currentKeMu = KeMu
        self.showMingxiTable()

    def showMingxiTable(self):
        n = self.msTable.rowCount()
        for i in range(n):
            self.msTable.removeRow(0)

        qijian = self.durationCbox.currentData(Qt.UserRole)
        KeMu = self.currentKeMu
        if KeMu == None:
            return
        fuzhu = self.fuzhuCbox.currentData(Qt.UserRole)

        items,yue_col = getMingxiAccount(KeMu[0],qijian,fuzhu)

        n = 0
        for item in items:
            self.msTable.setRowCount(n+1)
            self.showOneLine(n,item,yue_col[n])
            n = n+1
        return
    
    def showOneLine(self,row,data,yue):
        self.msTable.setItem(row,0,QTableWidgetItem(data[0]))
        item1 = QTableWidgetItem(str(data[1]))
        item1.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        self.msTable.setItem(row,1,item1)
        self.msTable.setItem(row,2,QTableWidgetItem(data[2]))
        text3 = "" if data[3] == 0 else "%.2f"%(data[3]/100)         
        item3 = QTableWidgetItem(text3)
        item3.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.msTable.setItem(row,3,item3)
        text4 = "" if data[4] == 0 else "%.2f"%(data[4]/100)
        item4 = QTableWidgetItem(text4)
        item4.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)        
        self.msTable.setItem(row,4,item4)
        text5 = "借" if yue>0 else "平" if yue == 0 else "贷"
        item5 = QTableWidgetItem(text5)
        item5.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)        
        self.msTable.setItem(row,5,item5)
        text6 = "%.2f"%(yue/100) if yue>0 else "%.2f"%(-yue/100)
        item6 = QTableWidgetItem(text6)
        item6.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)        
        self.msTable.setItem(row,6,item6)

    def frashBtnClicked(self):
        utils.initKeMuTreeWidget(self.kemuTree)
        self.kemuTree.currentItemChanged.disconnect(self.accountChanged)
        self.showMingxiTable()
        self.kemuTree.currentItemChanged.connect(self.accountChanged)


    def onPreviewClicked(self):

        qijian = self.durationCbox.currentData(Qt.UserRole)
        KeMu = self.currentKeMu
        if KeMu == None:
            return
        fuzhu = self.fuzhuCbox.currentData(Qt.UserRole)

        myprinter = printer.MyPrinter("mx") 
        myprinter.qijian = qijian 
        myprinter.kemu = KeMu
        myprinter.fuzhu = fuzhu
        myprinter.preview(self)






