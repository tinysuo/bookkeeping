
import os
import sqlite3
import config

import utils

def msgbox(title,msg):
    utils.msgbox(title,msg)


#由科目uudi获取是否挂了辅助,以及辅助项
def getKemuFuzhu(uuid):
    ret = [0,None]
    sql = "SELECT 辅助 FROM 科目表 WHERE uuid=?"
    cursor = config.sql_conn.cursor()
    try:
        cursor.execute(sql,[uuid])
        row = cursor.fetchone()
    except BaseException as e:
        msgbox("提示",str(e))
        return ret   
    cursor.close()    
    if row == None:
        msgbox("提示","没有找到对应的科目 by:"+uuid)
        return ret
    if row[0] == None or row[0] == "":
        return ret
    else:
        ret[0] = 1
    
    sql2 = "SELECT 辅助 FROM 辅助项目表 WHERE 类别=?"
    cursor = config.sql_conn.cursor()
    try:
        cursor.execute(sql2,[row[0]])
        items = cursor.fetchall()
    except BaseException as e:
        msgbox("提示",str(e))
        return ret   
    cursor.close() 

    fzs = []
    for item in items:
        fzs.append(item[0])
    ret[1] = fzs
    return ret
#从uuid获取科目代码和名称
def getKemuCodeName(uuid):
    ret = []
    sql = "SELECT 代码,名称 FROM 科目表 WHERE uuid=?"
    cursor = config.sql_conn.cursor()
    try:
        cursor.execute(sql,[uuid])
        row = cursor.fetchone()
    except BaseException as e:
        msgbox("提示",str(e))
    cursor.close() 
    if row == None:
        msgbox("提示","没有找到对应的科目 by:"+uuid)
        return
    ret.append(row[0])
    ret.append(row[1])
    return ret
#获了所有父科目，包括自己
def getPrentKemus(uuid):
    kemus = [uuid]
    sql = "SELECT 父uuid FROM 科目表 WHERE uuid=?"
    cursor = config.sql_conn.cursor()
    temp_uuid = uuid 
    while True:
        try:
            cursor.execute(sql,[temp_uuid])
            row = cursor.fetchone()
        except BaseException as e:
            msgbox("提示",str(e))
            return kemus
        if row == None:
            break
        temp_uuid = row[0]
        if temp_uuid == None:
            break
        kemus.append(temp_uuid)
    cursor.close()

    return kemus
#根据uuid获取凭证号
def getPzNobyuuid(uuid):
    sql = "SELECT 凭证号,凭证日期 FROM 凭证表 WHERE uuid=?"
    cursor = config.sql_conn.cursor()
    try:
        cursor.execute(sql,[uuid])
        row = cursor.fetchone()
    except BaseException as e:
        msgbox("提示",str(e))    
        return 
    cursor.close() 
    if row == None:
        msgbox("提示","没有找到对应的科目 by:"+uuid)
        return
    return row[0],row[1]
#反记账
def unRecodeKeeping(pzuuid):

    try: 
        cursor = config.sql_conn.cursor()  
        sql2 = "DELETE FROM 明细表 WHERE 凭证uuid=?"           
        cursor.execute(sql2,[pzuuid])
        #设置已经记账
        sql2 = "UPDATE 凭证表 SET 记账=0 WHERE uuid=?"
        cursor = config.sql_conn.cursor()   
        cursor.execute(sql2,[pzuuid])
        cursor.close()

    except BaseException as e:
        msgbox("提示",str(e))
        return
    config.sql_conn.commit() 
    msgbox("成功","反记账成功") 
#记账
def record_keeping(pzuuid):
    '''记账，参数为凭证的uuid'''
    try:   
        #如果已经记账，不再重复记账
        sql = "SELECT 凭证uuid FROM 明细表 WHERE 凭证uuid=?"
        cursor = config.sql_conn.cursor()   
        cursor.execute(sql,[pzuuid])
        ret = cursor.fetchall()
        if len(ret) > 0:
            msgbox("提示","当前凭证已经记账请不要重复记账")
            return
        #找到所有分录 
        sql1 = "SELECT 凭证uuid,摘要,科目uuid,借方金额,贷方金额,辅助 FROM 分录表 WHERE 凭证uuid=?"        
        cursor.execute(sql1,[pzuuid])
        result = cursor.fetchall()
        cursor.close()
    except BaseException as e:
        msgbox("提示",str(e))
        return
    
    #记入对应科目
    try: 
        cursor = config.sql_conn.cursor()  
        sql2 = "INSERT INTO 明细表 \
            (凭证号,凭证uuid,凭证日期,分录摘要,科目uuid,借方金额,贷方金额,辅助) \
            VALUES (?,?,?,?,?,?,?,?)"           
        for fl in result:
            #取当前科目的所有父科目，因为要记账到所有父科目        
            kemus = getPrentKemus(fl[2])
            pzNo,pzDate = getPzNobyuuid(pzuuid)     
            for km in kemus:
                cursor.execute(sql2,[pzNo,pzuuid,pzDate,fl[1],km,fl[3],fl[4],fl[5]])

        #设置已经记账
        sql2 = "UPDATE 凭证表 SET 记账=1 WHERE uuid=?"
        cursor = config.sql_conn.cursor()   
        cursor.execute(sql2,[pzuuid])
        cursor.close()

    except BaseException as e:
        msgbox("提示",str(e))
        return
    config.sql_conn.commit() 
    msgbox("成功","记账成功")       
#保存凭证和分录
def dbSavePingzheng(pz_info,fl_info):
    is_new = 0
    cursor = config.sql_conn.cursor()    
    #凭证是否已经存在,存在就更新
    try:        
        sql = "SELECT 记账 FROM 凭证表 WHERE uuid=?"
        cursor.execute(sql,[pz_info[0]])
        record = cursor.fetchall()
        if len(record) == 0:
            is_new = 1
        elif record[0][0] == 1:
            msgbox("提示","已记账凭证不能再次修改,要修改请先反记账")
            return 0
        if is_new == 0:#不是新的,
            sql = "UPDATE 凭证表 SET uuid=?,凭证号=?,凭证日期=?,摘要=?, \
                编辑时间=date('now'),附件数=?  WHERE uuid=?"
            pz_info.append(pz_info[0])
        else:
            sql = "INSERT INTO 凭证表 (uuid,凭证号,凭证日期,摘要,编辑时间,附件数) \
            VALUES (?,?,?,?,date('now'),?)"
        
        cursor.execute(sql,pz_info)


        #如果是更新,要删除原来所有此凭证的分录
        if is_new == 0: 
            sql = "DELETE FROM 分录表 WHERE 凭证uuid=?"
            cursor.execute(sql,[pz_info[0]])
        for rec in fl_info:
            sql2 = "INSERT INTO 分录表 (uuid,凭证uuid,摘要,科目uuid,借方金额,贷方金额,辅助) \
                    VALUES (?,?,?,?,?,?,?)"
            cursor.execute(sql2,rec)    
                             
    except BaseException as e:
        QMessageBox.warning(None,"提示",str(e),QMessageBox.Ok)
        return 0
    cursor.close() 
    config.sql_conn.commit()
    msgbox("成功","当前凭证保存成功")
    return 1
#获取所有会计期间
def getDurations():
    sql = "SELECT id,名称,开始,结束 FROM 会计期间表"
    conn = config.sql_conn
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        rec = cursor.fetchall()
        cursor.close
    except BaseException as e:
        msgbox("提示",str(e))    
        return 
    return rec 
#获取某日期所在的会计
def getDuration(date):
    #根据日期获取会计期间
    sql = "SELECT id,名称,开始,结束 FROM 会计期间表 WHERE 开始 <= ?  AND 结束 >= ?"
    conn = config.sql_conn
    cursor = conn.cursor()
    try:
        cursor.execute(sql,[date,date])
        rec = cursor.fetchone()
    except BaseException as e:
        msgbox("提示",str(e))    
        return 
    cursor.close
    if rec == None:
        msgbox("提示","当前日期不在已知的会计期间内")    
        return
    return rec 
#猎取当前日期会计期间的最大凭证号
def getMaxPZ_No(date):
    qijian = getDuration(date)
    #查询当前会计期间的最大凭证号    
    sql = "SELECT max(凭证号) FROM 凭证表 WHERE 凭证日期 >= ? AND 凭证日期 <= ?"
    conn = config.sql_conn
    cursor = conn.cursor()
    try:
        cursor.execute(sql,[qijian[2],qijian[3]])
        ret = cursor.fetchone()
        cursor.close
    except BaseException as e:
        msgbox("提示",str(e))    
        return 0
    if ret[0] == None:
        return 0
    return ret[0]
#取当前日期所在会计期间的所有凭证列表
def dbGetPingZhengList(date):
    qijian = getDuration(date)  
    sql = "SELECT 凭证号,凭证日期,摘要,附件数,记账,uuid FROM 凭证表 \
              WHERE 凭证日期 >= ? AND 凭证日期 <= ?"
    conn = config.sql_conn
    cursor = conn.cursor()
    try:
        cursor.execute(sql,[qijian[2],qijian[3]])
        ret = cursor.fetchall()
        cursor.close
    except BaseException as e:
        msgbox("提示",str(e))    
        return 
    return ret

def dbGetPingZhengInfo(uuid): 
    sql = "SELECT 凭证号,凭证日期,摘要,附件数,记账 FROM 凭证表 WHERE uuid = ?"
    conn = config.sql_conn
    cursor = conn.cursor()
    try:
        cursor.execute(sql,[uuid])
        ret = cursor.fetchone()
        cursor.close
    except BaseException as e:
        msgbox("提示",str(e))    
        return 
    return ret    

#由科目代码取科目信息
def getKumuByCode(code):
    sql = "SELECT uuid,代码,名称,辅助 FROM 科目表 WHERE 代码=?"
    cursor = config.sql_conn.cursor()
    try:
        cursor.execute(sql,[code])
        row = cursor.fetchone()
        cursor.close
    except BaseException as e:
        msgbox("提示",str(e))
        return
    if row == None:
        msgbox("提示","没有找到对应的科目 by:"+code)
        return
    return row
#获取明细账,参数科目uuid,会计期间
def getMingxiAccount(kmuuid,qijian,fuzhu):
    [jie,dai] = getBigenValue(kmuuid,qijian,fuzhu) #取上期余额
    start = [qijian[2],"","上期余额",jie,dai]

    sql = "SELECT 凭证日期,凭证号,分录摘要,借方金额,贷方金额 FROM 明细表  \
          WHERE 科目uuid = ? AND 凭证日期 >= ? AND 凭证日期 <= ?  "
    if fuzhu != None and fuzhu != "": 
        sql += "AND  辅助 = '%s'"%fuzhu
    sql +=  " ORDER BY 凭证号 "  
    cursor = config.sql_conn.cursor()
    try:
        cursor.execute(sql,[kmuuid,qijian[2],qijian[3]])
        items = cursor.fetchall()
        cursor.close
    except BaseException as e:
        msgbox("提示",str(e))
        return
    cursor.close() 
    本期借方 = 0
    本期贷方 = 0
    for item in items:
        本期借方 += item[3]
        本期贷方 += item[4]

    items.insert(0,start)
    
    col_yue = []
    yue = 0
    for item in items:
        yue = yue + item[3] - item[4]
        col_yue.append(yue)

    end1 = ["","","本期合计",本期借方,本期贷方,yue]
    end2 = ["","","累积合计",本期借方+jie,本期贷方+dai,yue]
    items.append(end1)
    items.append(end2)
    col_yue.append(yue)
    col_yue.append(yue)

    return items,col_yue
#获取凭证的所有分录 
def getFengluByPingzheng(uuid):
    sql = "SELECT uuid,摘要,科目uuid,借方金额,贷方金额,辅助 FROM 分录表 WHERE 凭证uuid=?"
    conn:sqlite3.Connection = config.sql_conn
    try:
        cursor= conn.cursor()
        cursor.execute(sql,[uuid])
        result = cursor.fetchall()
        cursor.close()
    except BaseException as e:
        msgbox("提示",str(e))
        return []

    return result
#获取期初余额数据，包括本会计期间之前发生额 参数科目uuid,会计期间
def getBigenValue(kmuuid,qijian,fuzhu):
    jie = 0
    dai = 0
    #取之前所有此科目的发生额,用于计算
    sql2 = "SELECT 借方金额,贷方金额 FROM 明细表 WHERE 科目uuid=? AND  凭证日期 < ? " 
    if fuzhu != None and fuzhu != "":
        sql2 += " AND 辅助='%s' "%fuzhu
    cursor = config.sql_conn.cursor()
    try:
        cursor.execute(sql2,[kmuuid,qijian[2]])
        items = cursor.fetchall()
        cursor.close
    except BaseException as e:
        msgbox("提示",str(e))
        return
    for item in items:
        jie += item[0]
        dai += item[1]
    return [jie,dai]
#保存电子附件
def saveFujianFile(uuid,filename):
    file = open(filename, 'rb')
    if file == None:
        msgbox("提示","文件不存在")
        return 
    data = file.read()
    file.close()
    
    name = os.path.basename(filename)
    format = os.path.splitext(name)[-1]

    sql = "INSERT INTO 电子附件表 (凭证uuid,文件名, 格式, 数据) VALUES (?, ?, ?, ?)"
    cursor = config.sql_conn.cursor()
    try:
        cursor.execute(sql,(uuid,name,format,data))
        cursor.close
        config.sql_conn.commit()
    except BaseException as e:
        msgbox("提示",str(e))
        return   

def getFujianList(uuid):
    sql = "SELECT id,文件名,格式 FROM 电子附件表 WHERE 凭证uuid = ?"
    conn = config.sql_conn
    cursor = conn.cursor()
    try:
        cursor.execute(sql,[uuid])
        items = cursor.fetchall()
        cursor.close
    except BaseException as e:
        msgbox("提示",str(e))    
        return 
    return  items
 
def getFujianData(id):
    sql = "SELECT 格式,数据 FROM 电子附件表 WHERE id = ?"
    conn = config.sql_conn
    cursor = conn.cursor()
    try:
        cursor.execute(sql,[id])
        item = cursor.fetchone()
        cursor.close
    except BaseException as e:
        msgbox("提示",str(e))    
        return 
    return  item

def removeFujianOnDB(id):
    sql = "DELETE FROM 电子附件表 WHERE id=?"
    conn = config.sql_conn
    cursor = conn.cursor()
    try:
        cursor.execute(sql,[id])
        item = cursor.fetchone()
        cursor.close
        conn.commit()
    except BaseException as e:
        msgbox("提示",str(e))    
        return 

def getbookParam(key:str):

    sql = "SELECT data FROM 参数表 WHERE key = ?"
    conn = config.sql_conn
    cursor = conn.cursor()
    try:
        cursor.execute(sql,[key])
        item = cursor.fetchone()
        cursor.close
    except BaseException as e:
        msgbox("提示",str(e))    
        return ""  
    if item == None:
        return ""
    else:
        return  item[0]

def setBookParam(conn:sqlite3, key:str,data:str):
    sql = "UPDATE 参数表 SET data=? WHERE key = ?"
    cursor = conn.cursor()
    try:
        cursor.execute(sql,[data,key])
        cursor.close()
    except BaseException as e:
        msgbox("提示",str(e))    
        return -1  
    return 0

#取科目链父子科目,用于是烤漆
def getPrentChildKuMu(names:list,kmuuid):

    sql = "SELECT 代码,名称,父uuid FROM 科目表 WHERE uuid=?"
    cursor = config.sql_conn.cursor()
    try:
        cursor.execute(sql,[kmuuid])
        row = cursor.fetchone()
        cursor.close()         
    except BaseException as e:
        msgbox("提示",str(e))
        return
    if row == None:
        msgbox("提示","没有找到对应的科目 by:"+kmuuid)
        return
    names.insert(0,row[1])
    if row[2] != "":
        getPrentChildKuMu(names,row[2])
    return

def getKeMuLable(uuid):
    names = list()
    getPrentChildKuMu(names,uuid)
    kemu = getKemuCodeName(uuid)
    if len(names) > 0:
        nameText = ""
        for name in names:
            nameText += "-"+name
    return kemu[0] + nameText

def getLastDuration():
    sql = "SELECT id,名称,开始,结束 FROM 会计期间表 ORDER BY 结束 DESC LIMIT 1"
    conn = config.sql_conn
    ret = []
    try:
        cursor = conn.cursor()        
        cursor.execute(sql)
        ret = cursor.fetchone()
        cursor.close()
    except BaseException as e:
        msgbox("提示",str(e))    
        return []  
    return ret

def durationIsUsed(duration):
    sql = "SELECT count (*) FROM 凭证表 WHERE 凭证日期 >= ? AND 凭证日期 <= ?"
    conn = config.sql_conn
    cursor = conn.cursor()
    try:
        cursor.execute(sql,[duration[2],duration[3]])
        ret = cursor.fetchone()
        cursor.close
    except BaseException as e:
        msgbox("提示",str(e))    
        return 0
    return ret[0]

def delDuration(id):
    sql = "DELETE FROM 会计期间表 WHERE id=?"
    conn = config.sql_conn
    cursor = conn.cursor()
    ndel = 0
    try:
        cursor.execute(sql,[id])
        cursor.close
        conn.commit()
        ndel = conn.total_changes
    except BaseException as e:
        msgbox("提示",str(e))    
        return 0

def newFreeDuration(duration):
    date1 = datetim