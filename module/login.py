
import sys, os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import hashlib
import config
import json
import sqlite3
import utils
import newBookDlg

class LoginDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('欢迎使用蚂蚁记账')  # 设置标题
        self.setGeometry(500,200,600,400)

        self.setWindowIcon(QIcon(config.app_home+"/images/logo64.png"))
        #居中
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)
        self.user_dict = {}
        '''
        定义界面控件设置
        '''
        self.verticalLayout = QVBoxLayout(self)  # 设置横向布局
        self.verticalLayout.setContentsMargins(40,10, 50, 10)
        self.verticalLayout.addStretch(1)
        self.verticalLayout.setSpacing(20)

        self.topLayout = QHBoxLayout()
        self.verticalLayout.addLayout(self.topLayout)
        banner = QLabel("")
        self.topLayout.addStretch(1)
        self.topLayout.addWidget(banner)
        self.topLayout.addStretch(1)
        banner.setPixmap(QPixmap(config.app_home+"/icon/banner.png"))

        self.newbookBtn = QPushButton("")
        self.newbookBtn.setObjectName("newBookBnt")
        self.newbookBtn.setFlat(True)
        self.newbookBtn.setIconSize(QSize(32,32))
        self.newbookBtn.setIcon(QIcon(config.app_home+"/icon/newbook.svg"))
        #self.topLayout.addWidget(self.newbookBtn)
        self.topLayout.setStretch(2,1)

        
        self.formlayout = QFormLayout()
        self.formlayout.setContentsMargins(0,0,50,0)
        self.formlayout.setLabelAlignment(Qt.AlignRight)
  
        self.book_cbox = QComboBox()
        self.initBookCbox()
        
        self.book_cbox.setStyleSheet("padding: 6px;")
        
        self.dateedit = QDateEdit()
        self.dateedit.setDate(QDate.currentDate())
        self.dateedit.setToolTip("日期决定了记账的会计期间")
        self.dateedit.setStyleSheet("padding: 6px;")
              
        self.passwd = QLineEdit()  # 定义密码输入框
        self.passwd.setPlaceholderText("请输入登录密码")  # 设置默认显示的提示语
        self.passwd.setEchoMode(QLineEdit.Password)
        self.passwd.setStyleSheet("padding: 6px;")
        self.button_enter = QPushButton()  # 定义登录按钮
        self.button_enter.setText("登录")  # 按钮显示值为登录
        self.button_enter.setMinimumSize(60, 40)   

        self.button_quit = QPushButton()  # 定义返回按钮
        self.button_quit.setText("退出")  # 按钮显示值为返回
        self.button_quit.setMinimumSize(60, 40)

        self.button_enter.setIcon(QIcon(config.app_home+"/icon/login.svg"))
        self.button_quit.setIcon(QIcon(config.app_home+"/icon/logout.svg"))         
        
        self.formlayout.addRow("账套", self.book_cbox)
        self.formlayout.addRow("账期", self.dateedit)
        self.formlayout.addRow("密码", self.passwd)
        self.formlayout.addRow("", self.button_enter)
        self.formlayout.addRow("", self.button_quit)
        self.prompt_msg = QLabel("")
        self.prompt_msg.setAlignment(Qt.AlignCenter)
        self.prompt_msg.setObjectName("prompt_msg")
        self.formlayout.addRow("", self.prompt_msg)

        self.verticalLayout.addLayout(self.formlayout)   
        self.verticalLayout.addStretch(1)

        btmLayout = QHBoxLayout()
        self.verticalLayout.addLayout(btmLayout)
        btmLayout.addStretch(1)
        btmLayout.addWidget(self.newbookBtn)
 

        # 绑定按钮事件
        self.newbookBtn.clicked.connect(self.newButtonClicked)
        self.button_enter.clicked.connect(self.button_enter_verify)
        self.button_quit.clicked.connect(
            QCoreApplication.instance().quit)  # 返回按钮绑定到退出
        
        self.passwd.setFocus()

    def initBookCbox(self):
        self.book_cbox.clear()
        dst_path = config.app_home +'/账套'
        for file in os.listdir( dst_path ):
            if file.endswith( '.db' ):
                self.book_cbox.addItem(os.path.splitext(file)[0])
        json_file =  config.app_home +'/账套/config.json'   
        with open(json_file, 'r',encoding='UTF-8') as f:
            jobj = json.loads(f.read())
        self.book_cbox.setCurrentIndex(jobj['db_index'])

    def newButtonClicked(self):
        dlg = newBookDlg.newBookDlg(self)
        dlg.exec()
        self.initBookCbox()

    def button_enter_verify(self):
        # 校验账号是否正确
        cfg = {'db_index':self.book_cbox.currentIndex()}
        json_file =  config.app_home +'/账套/config.json'   
        with open(json_file, 'w',encoding='UTF-8') as f:
            json.dump(cfg,f)
        passwd = self.passwd.text()
        config.kj_date = self.dateedit.date()

        pwd2 = ("ant account" + passwd).encode('utf-8')
        sh256 = hashlib.sha256(pwd2).hexdigest()
        #print(sh256)
        db_name = self.book_cbox.currentText()
        if db_name == "":
            return
        config.db_name = db_name
        db_file = config.app_home+"/账套/"+db_name+".db"
        try:
            conn = sqlite3.connect(db_file)
            config.sql_conn = conn
            conn.executescript("PRAGMA key='%s'"%(sh256))
            cursor = conn.cursor()
            cursor.execute("SELECT col FROM test")
            val = cursor.fetchone()
        except:
            QMessageBox.warning(self,"提示","打开账套失败.",QMessageBox.Ok)
            self.prompt_msg.setText("打开数据库出错")
            return
        if val[0] == "ant":
            self.accept()
        else:
            self.prompt_msg.setText("打开数据库出错")
            return
        
