import sys, os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import config
import hashlib
import sqlite3
import dbfunc
import datetime
import tempfile
import shutil

def msgbox(title,msg):
    QMessageBox.warning(None,title,msg,QMessageBox.Ok)

class newBookDlg(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('新建账套')  # 设置标题
        self.setGeometry(500,200,800,600)

        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)

        self.vLayout = QVBoxLayout(self)  # 设置横向布局
        self.vLayout.setContentsMargins(100,50, 100, 50)

        self.formlayout = QFormLayout()
        self.vLayout.addLayout(self.formlayout)

        self.hLayout = QHBoxLayout()
        rejectBTN = QPushButton("取消")
        newBTN = QPushButton("新建")
        self.hLayout.addWidget(rejectBTN)
        self.hLayout.addWidget(newBTN)
        self.vLayout.addLayout(self.hLayout)

        rejectBTN.clicked.connect(self.rejetcBTNClicked)
        newBTN.clicked.connect(self.newBTNClicked)
        self.initFormlayout()

    def initFormlayout(self):
        #初始化表单layout
        self.editBookname = QLineEdit()
        self.formlayout.addRow("账套名称", self.editBookname)

        self.会计准则列表 = QComboBox()
        self.会计准则列表.addItems(["事业单位","小企业","中小学食堂"])
        self.formlayout.addRow("会计准则", self.会计准则列表)
        self.会计期间列表 = QComboBox()
        self.会计期间列表.addItems(["自然月","自由期间"])
        self.会计期间列表.setCurrentText("自然月")
        self.formlayout.addRow("会计期间", self.会计期间列表)
        self.启用时间 = QDateEdit()
        self.formlayout.addRow("启用时间", self.启用时间)
        self.编码方案 = QLineEdit()
        self.formlayout.addRow("编码方案", self.编码方案)
        self.adminPassword = QLineEdit()
        self.formlayout.addRow("管理员密码", self.adminPassword)
        self.adminPassword2 = QLineEdit()
        self.formlayout.addRow("确认密码", self.adminPassword2)

        self.formlayout.addRow("单位参数：",None)
        self.单位名称 = QLineEdit()
        self.formlayout.addRow("单们名称", self.单位名称)
        self.财务主管 = QLineEdit()
        self.formlayout.addRow("财务主管", self.财务主管)
        self.会计 = QLineEdit()
        self.formlayout.addRow("会计", self.会计)
        self.出纳 = QLineEdit()
        self.formlayout.addRow("出纳", self.出纳)

        self.formlayout.setLabelAlignment(Qt.AlignRight)

        self.编码方案.setText("4-2-2")
        self.编码方案.setDisabled(True)
        self.会计准则列表.setCurrentText("事业单位会计准则")
        self.启用时间.setDate(QDate.currentDate())    

    def rejetcBTNClicked(self):
        aaa = 0
        info_dict = {}
        info_dict["启用时间"] = "2023-09-01"
        self.initDuration(None,info_dict)

    def newBTNClicked(self):
        name = self.editBookname.text()
        passwd1 = self.adminPassword.text()
        passwd2 = self.adminPassword2.text()
        if passwd1 != passwd2:
            msgbox("出错了","两次密码输入不同，请正确设置密码")
            return
        infodict = {}
        infodict["会计准则"] = self.会计准则列表.currentText()
        infodict["会计期间"] = self.会计期间列表.currentText()
        infodict["启用时间"] = self.启用时间.date().toString("yyyy-MM-dd")
        infodict["编码方案"] = self.编码方案.text()
        infodict["单位名称"] = self.单位名称.text()
        infodict["财务主管"] = self.财务主管.text()
        infodict["会计"] = self.会计.text()
        infodict["出纳"] = self.出纳.text()

        ret = self.newAccountBook(name,passwd1,infodict)
        if ret == 0:
            self.accept()
        
    #新建数据库，设置密码，建立所需要的表
    def newAccountBook(self,name:str,psword:str,info_dict):
        try:
            #已经存在提醒
            dbfile = "%s/账套/%s.db"%(config.app_home,name)
            if os.path.exists(dbfile):
                msgbox("提示","账套文件已经存在，请使用不同的账套名")
                return -1
            #建库
            pwd2 = ("ant account" + psword).encode('utf-8')
            sha = hashlib.sha256(pwd2)

            tmp = tempfile.mkstemp(prefix = ".db")
            conn = sqlite3.connect(tmp[1])

            conn.executescript("PRAGMA key='%s'"%(sha.hexdigest()))
            #conn.execute("PRAGMA key='%s'"%(psword))
            conn.execute('create table test(col text)')
            conn.execute("insert into test values('ant')")
            #建表
            sqlfile = config.app_home+"/script/newbook.sql"
            with open(sqlfile, 'r',encoding='UTF-8') as f:
                sql_all = f.read()
            conn.executescript(sql_all)
            
            dbfunc.setBookParam(conn,"会计准则",info_dict["会计准则"])
            dbfunc.setBookParam(conn,"会计期间",info_dict["会计期间"])
            dbfunc.setBookParam(conn,"启用时间",info_dict["启用时间"])
            dbfunc.setBookParam(conn,"编码方案",info_dict["编码方案"])
            dbfunc.setBookParam(conn,"单位名称",info_dict["单位名称"])
            dbfunc.setBookParam(conn,"财务主管",info_dict["财务主管"])
            dbfunc.setBookParam(conn,"会计",info_dict["会计"])
            dbfunc.setBookParam(conn,"出纳",info_dict["出纳"])
        
            #插入预设数据
            print("开始初始化会计要素与预设科目")
            script = info_dict["会计准则"]
            scriptfile = config.app_home+"/script/%s.sql"%(script)
            print(scriptfile)
            with open(scriptfile, 'r',encoding='UTF-8') as f:
                sql = f.read()
            conn.executescript(sql)

            #初始化会计期间
            ret = self.initDuration(conn,info_dict)

            conn.commit()
            conn.close()
            if ret == 0:
                shutil.copyfile(tmp[1],dbfile)
        except BaseException as e:
            msgbox("提示",str(e))
            return -1
        return 0
    
    def initDuration(self,conn,info_dict):
        #确定启用年和月
        strDuration = info_dict["启用时间"]
        start_date = datetime.date.fromisoformat(strDuration)
        #生成初始余额会计期间
        date2 = datetime.date(year=start_date.year,month = start_date.month,day=1) +datetime.timedelta(days=-1)     
        date1 = datetime.date(date2.year,date2.month,1)

        sql = "INSERT INTO 会计期间表 (名称,开始,结束) VALUES(?,?,?)"

        try:
            cursor = conn.cursor()
            cursor.execute(sql,("期初余额设置期",date1.strftime("%Y-%m-%d"),date2.strftime("%Y-%m-%d")))
            if info_dict["会计期间"] == "自然月":
                for mm in range(start_date.month,13):
                    date_s = datetime.date(year=start_date.year,month = mm,day=1)
                    date_e = date_s + datetime.timedelta(days=31) 
                    date_e = datetime.date(date_e.year,date_e.month,1)+datetime.timedelta(days=-1)
                    name = "%d年%d月份"%(date_s.year,date_s.month)
                    cursor.execute(sql,(name,date_s.strftime("%Y-%m-%d"),date_e.strftime("%Y-%m-%d")))
            elif info_dict["会计期间"] == "自由期间":
                cursor.execute(sql,("会计期间一",start_date.strftime("%Y-%m-%d"),"2099-12-31"))
        except BaseException as e:
            msgbox(str(sys._getframe().f_lineno),str(e))
            return -1
        return 0



