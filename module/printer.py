

import sys, os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *
import config
from dbfunc import *
import datetime

class MyPrinter:
    def __init__(self,type):
        self.type = type
        self.printer = QPrinter()
        if type == "pz":
            self.initPingZhengPrinter()
        elif type == "mx":
            self.initMingXiPrinter()

        self.qijian = None
        self.kemu = None
        self.fuzhu = None
    def initPingZhengPrinter(self):
        #读取保存的参数初始化打印机
        self.printer.setPageSize(QPrinter.A4)
        self.printer.setOrientation(QPrinter.Landscape)
        #self.printer.setMargins(QMargins(144,72,72,72))
        self.printer.setFullPage(True)

    def initMingXiPrinter(self):
        #读取保存的参数初始化打印机
        self.printer.setPageSize(QPrinter.A4)
        self.printer.setOrientation(QPrinter.Landscape)
        #self.printer.setMargins(QMargins(144,72,72,72))
        self.printer.setFullPage(True)

    def print(self):
        self.render(self.printer)

    def preview(self,parent):
        preview_dialog = QPrintPreviewDialog(self.printer,parent)  
        #preview_dialog.setWindowIcon(self,QIcon(config.app_home+"/images/logo256.png"))    
        preview_dialog.setWindowTitle("Print Preview")
        preview_dialog.resize(800, 600)
        preview_dialog.paintRequested.connect(self.render)
        preview_dialog.exec_()

    def render(self,printer):       
        if self.type =="pz":
            self.renderPingzheng(printer)
        elif self.type == "mx":
            self.renderMingxi(printer)

    def renderPingzhengPage(self,printer:QPrinter,painter,pzInfo,rows,page,pages):
        dpi = printer.resolution()

        leftm = dpi/2.54*5
        topm = dpi/2.54*2.5
        rightm = dpi/2.54*2.5
        buttom = dpi/2.54*2.5

        rect = painter.viewport()

        win = painter.window()

        width = rect.width()
        height = rect.height()


        viewWidth = width - leftm - rightm
        viewHeight = height - topm - buttom
        xrate = [0.35,0.35,0.15,0.15]
        xpos = [leftm,0,0,0,0,0]
        ypos = [topm,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        for i in range(0,4):
            xpos[i+1] = xpos[i] + viewWidth*xrate[i]
        for i in range(0,14):
            ypos[i+1] = ypos[i] + viewHeight/12


        painter.setFont(QFont('SimSun', 25))
        rect_title = QRect(xpos[0],ypos[0],viewWidth,viewHeight//12)
        painter.drawText(rect_title,Qt.AlignHCenter | Qt.AlignTop,"记  账  凭  证")

        painter.setFont(QFont('SimSun', 14))
        painter.drawText(rect_title,Qt.AlignRight | Qt.AlignBottom,"凭证号：%d"%(pzInfo[0]))        
        rect_danwei = QRect(xpos[0],ypos[1]-5,viewWidth,viewHeight//12)
        dw_name = getbookParam("单位名称")    
        painter.drawText(rect_danwei,Qt.AlignLeft | Qt.AlignBottom,"单位名称：%s"%(dw_name))
        painter.drawText(rect_danwei,Qt.AlignRight | Qt.AlignBottom,"附件 %d 张"%(pzInfo[3]))       
        rect_date = QRect(xpos[0],ypos[1],viewWidth,viewHeight//12)
        date_text = datetime.date.fromisoformat(pzInfo[1]).strftime("%Y 年 %m 月 %d 日")
        painter.drawText(rect_date,Qt.AlignHCenter | Qt.AlignTop,date_text)
        rect_bottom = QRect(xpos[0],ypos[11],viewWidth,viewHeight//12)
        painter.drawText(rect_bottom,Qt.AlignLeft | Qt.AlignVCenter,"财务主管：%s  \t会计:%s     \t出纳:%s"\
                         %(getbookParam("财务主管"),getbookParam("会计"),getbookParam("出纳")))
        painter.drawText(rect_bottom,Qt.AlignRight | Qt.AlignVCenter,"第 %d 页共 %d 页 "%(page+1,pages))  

        painter.setFont(QFont('SimSun', 18))
        rect_head =  QRect(xpos[0],ypos[2],xpos[1]-xpos[0] ,viewHeight//12) 
        painter.drawText(rect_head,Qt.AlignHCenter | Qt.AlignVCenter,"摘要") 
        rect_head =  QRect(xpos[1],ypos[2],xpos[2]-xpos[1] ,viewHeight//12) 
        painter.drawText(rect_head,Qt.AlignHCenter | Qt.AlignVCenter,"科目")   
        rect_head =  QRect(xpos[2],ypos[2],xpos[3]-xpos[2] ,viewHeight//12) 
        painter.drawText(rect_head,Qt.AlignHCenter | Qt.AlignVCenter,"借方") 
        rect_head =  QRect(xpos[3],ypos[2],xpos[4]-xpos[3] ,viewHeight//12) 
        painter.drawText(rect_head,Qt.AlignHCenter | Qt.AlignVCenter,"贷方")  
        #输出分录项
        painter.setFont(QFont('SimSun', 12))

        sindex = page*7
        eindex = (page+1)*7
        if eindex > len(rows):
            eindex = len(rows)

        for i in range(sindex,eindex):
            line = i%7
            row = rows[i]
            lable = getKeMuLable(row[2])
            if row[5] != "":
                lable += "(%s)"%(row[5])
            ts = ["","","",""]
            ts[0] = row[1]; ts[1] = lable; 
            ts[2] = "￥%.2f"%(row[3]/100) if row[3] != 0 else ""
            ts[3] = "￥%.2f"%(row[4]/100) if row[4] != 0 else ""
            for j in range(0,4):
                rc =  QRect(xpos[j],ypos[3+line],xpos[j+1]-xpos[j] ,viewHeight//12) 
                align = Qt.AlignRight | Qt.AlignVCenter if j>1 else Qt.AlignLeft | Qt.AlignVCenter if j==1 else Qt.AlignHCenter | Qt.AlignVCenter
                painter.drawText(rc,align,ts[j])

        hj_jie = 0 ; hj_dai = 0
        for row in rows:
            hj_jie += row[3]
            hj_dai += row[4]
        if page < pages-1:
            text8 = "过次页"
            jie_text = ""
            dai_text = ""
        else:
            text8 = "合计"
            jie_text = "￥%.2f"%(hj_jie/100)
            dai_text = "￥%.2f"%(hj_dai/100)

        rc =  QRect(xpos[0],ypos[3+7],xpos[2]-xpos[0] ,viewHeight//12) 
        align =  Qt.AlignRight| Qt.AlignVCenter
        painter.drawText(rc,Qt.AlignHCenter | Qt.AlignVCenter,text8)
        rc =  QRect(xpos[2],ypos[3+7],xpos[3]-xpos[2] -5,viewHeight//12) 
        painter.drawText(rc,align,jie_text)
        rc =  QRect(xpos[3],ypos[3+7],xpos[4]-xpos[3] -5 ,viewHeight//12) 
        painter.drawText(rc,align,dai_text)


        pen = QPen(Qt.black, 2, Qt.SolidLine)
        painter.setPen(pen)
        painter.drawLine(xpos[0]+viewWidth//3, ypos[1]-7, xpos[4]-viewWidth//3, ypos[1]-7)
        painter.drawLine(xpos[0]+viewWidth//3, ypos[1]-5, xpos[4]-viewWidth//3, ypos[1]-5)

        painter.drawLine(xpos[0], ypos[2], xpos[4], ypos[2])  #第一横线
        painter.drawLine(xpos[0], ypos[11], xpos[4], ypos[11])#最下横线
        painter.drawLine(xpos[0], ypos[2], xpos[0], ypos[11]) #第一竖线
        painter.drawLine(xpos[4], ypos[2], xpos[4], ypos[11]) #最右竖线

        #画横线
        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
        for i in range(3,11):            
            painter.drawLine(xpos[0], ypos[i], xpos[4], ypos[i])
        painter.drawLine(xpos[1], ypos[2], xpos[1], ypos[10])
        painter.drawLine(xpos[2], ypos[2], xpos[2], ypos[11])
        painter.drawLine(xpos[3], ypos[2], xpos[3], ypos[11])
        painter.drawLine(xpos[4], ypos[2], xpos[4], ypos[11])

    def renderPingzheng(self,printer:QPrinter):
        pzInfo = dbGetPingZhengInfo(self.pzuuid)
        if pzInfo == None:
            return
        rows =getFengluByPingzheng(self.pzuuid)
        if len(rows) == 0:
            return
        pages = len(rows)//7
        if len(rows)%7 > 0:
             pages += 1

        painter = QPainter(printer)
        for page in range(0,pages):
            if page != 0:
                printer.newPage()
            self.renderPingzhengPage(printer,painter,pzInfo,rows,page,pages)
        painter.end() 

    def renderMingxi(self,printer):

        items,yues = getMingxiAccount(self.kemu[0],self.qijian,self.fuzhu)
        rpp = 28
        pages = len(items)//rpp
        if len(items)%rpp != 0:
            pages += 1
        painter = QPainter(printer)
        for page in range(0,pages):
            if page != 0:
                printer.newPage()
            self.renderMingXiPage(printer,painter,page,pages,items,yues)  
        painter.end()   

    def renderMingXiPage(self,printer,painter,page,pages,items,yues):
        
        print("page= ",page)
        dpi = printer.resolution()

        leftm = dpi/2.54*5
        topm = dpi/2.54*1
        rightm = dpi/2.54*2.5
        buttom = dpi/2.54*1

        rect = painter.viewport()
        win = painter.window()

        width = rect.width()
        height = rect.height()

        lines = 37
        viewWidth = width - leftm - rightm
        viewHeight = height - topm - buttom
        xrate = [0.08,0.04,0.04,0.08,0.35,0.10,0.10,0.06,0.15]
        xpos =[0]*10
        xpos[0] = leftm
        ypos = [0]*(lines+1)
        ypos[0] = topm
        for i in range(0,9):
            xpos[i+1] = xpos[i] + viewWidth*xrate[i]
        for i in range(0,lines):
            ypos[i+1] = ypos[i] + viewHeight/lines

        painter.setFont(QFont('SimSun', 25))
        rect_title = QRect(xpos[0],ypos[0],viewWidth,viewHeight/lines*2)
        painter.drawText(rect_title,Qt.AlignHCenter | Qt.AlignTop,"科 目 明 细 账")

        painter.setFont(QFont('SimSun', 10))

        sindex = page*27
        eindex = (page+1)*27
        if eindex > len(items):
            eindex = len(items)
        for i in range(sindex,eindex):
            item = items[i]; yue = yues[i]
            ts = ["2023","12","31","1","测试摘要111111","123.22","456.00","借","123456.00",""]
            ts[0] = item[0][0:4];   ts[1] = item[0][5:7];   ts[2] = item[0][8:10];
            ts[3] = str(items[i][1]);   ts[4] = items[i][2]
            ts[5] = "" if item[3] == 0 else "%.2f"%(item[3]/100)
            ts[6] = "" if item[4] == 0 else "%.2f"%(item[4]/100)
            ts[7] = "借" if yues[i]>0 else "平" if yues[i] == 0 else "贷"
            ts[8] = "%.2f"%(yue/100) if yue >= 0 else "%.2f"%(-yue/100)
            for j in range(0,9):
                align = Qt.AlignHCenter | Qt.AlignVCenter
                align = Qt.AlignLeft | Qt.AlignVCenter if j == 4 else Qt.AlignRight | Qt.AlignVCenter if j ==5 or j==6 or j==8 else Qt.AlignHCenter | Qt.AlignVCenter
                rect = QRect(xpos[j]+5,ypos[7+i],xpos[j+1] - xpos[j]-10,viewHeight/lines)
                painter.drawText(rect,align,ts[j])


        painter.setFont(QFont('SimSun', 12))
        #打印表头
        header = ["年","月","日","凭证号","摘要","借方","货方","方向","余额",""]
        for i in range(0,9):
            rect_h = QRect(xpos[i],ypos[5],xpos[i+1] - xpos[i],viewHeight/lines*2)
            painter.drawText(rect_h,Qt.AlignHCenter | Qt.AlignVCenter,header[i])

        rect_t1 = QRect(xpos[0],ypos[2],viewWidth,viewHeight/lines*2)
        painter.drawText(rect_t1,Qt.AlignHCenter | Qt.AlignVCenter,"%s(%s--%s)"%(self.qijian[1],self.qijian[2],self.qijian[3]))

        kemuLable = getKeMuLable(self.kemu[0])

        rect_t2 = QRect(xpos[0],ypos[3]-5,viewWidth,viewHeight/lines*2)
        painter.drawText(rect_t2,Qt.AlignLeft | Qt.AlignBottom,"科目：%s"%(kemuLable))
        painter.drawText(rect_t2,Qt.AlignRight | Qt.AlignBottom,"本页%d-%d 共%d笔"%(sindex+1,eindex,len(items)))

        ft1 = getbookParam("财务主管")
        ft2 = getbookParam("会计")
        ft3 = getbookParam("出纳")
        rect_foot = QRect(xpos[0],ypos[lines-2],viewWidth,viewHeight/lines*2)
        painter.drawText(rect_foot,Qt.AlignLeft | Qt.AlignVCenter,"财务主管:%s    会计:%s    出纳:%s"%(ft1,ft2,ft3))
        painter.drawText(rect_foot,Qt.AlignRight | Qt.AlignVCenter,"页码：第%d页 共%d页"%(page+1,pages))

        #画横线
        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
        painter.drawLine(xpos[0]+viewWidth/3, ypos[2], xpos[0]+viewWidth/3*2, ypos[2]) #标题下双线
        painter.drawLine(xpos[0]+viewWidth/3, ypos[2]-2, xpos[0]+viewWidth/3*2, ypos[2]-2) #标题下双线
        painter.drawLine(xpos[0], ypos[5], xpos[9], ypos[5]) #表格上边框
        for i in range(7,lines-1):            
            painter.drawLine(xpos[0], ypos[i], xpos[9], ypos[i])
        #画竖线
        for i in range(0,10):
            painter.drawLine(xpos[i], ypos[5], xpos[i], ypos[lines -2])


 



