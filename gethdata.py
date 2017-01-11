#User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36
#Cookie:PHPSESSID=mf81gbt9ua381me0d5aootkh75; ca=2; Hm_lvt_5b3c1a9996890ca7bb2c1fdcb46af3bf=1484129183; Hm_lpvt_5b3c1a9996890ca7bb2c1fdcb46af3bf=1484129324
#Host:www.cphui.com
#Referer:http://www.cphui.com/pk10

# {u'n10': 10, u'termNum': u'595519', u'lotteryTime': u'2017-01-02 23:57:00', u'n8': 9, u'n9': 4, u'n1': 5, u'n2': 8, u'n3': 2, u'n4': 1, u'n5': 6, u'n6': 3, u'n7': 7}

import requests,json,os,sqlite3
# url="http://www.cphui.com/pk10/getHistoryData?count=&date=2017-01-02&t=0.577461605231151"

headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36",
"Host":"www.cphui.com",
"Referer":"http://www.cphui.com/pk10",
#"Cookie":"PHPSESSID=mf81gbt9ua381me0d5aootkh75; ca=2; Hm_lvt_5b3c1a9996890ca7bb2c1fdcb46af3bf=1484129183; Hm_lpvt_5b3c1a9996890ca7bb2c1fdcb46af3bf=1484129324",
"X-Requested-With":"XMLHttpRequest"
}

def isTableExist(con,tablename):
	"""
	return 0 means  table is not existed
	"""
	sqlstr= "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s';" % tablename
	result=con.execute(sqlstr)
	result=int(result.fetchone()[0])
	return result
def createtable(con,tablename):
	"""
	 create table pk10 (
	 id integer primary key AUTOINCREMENT,
	 termNum text not null,
	 lotteryTime  text not null,
	 n10 text not null,
	 )
	"""
	if isTableExist(con,tablename)==0:
		sqlstr='''
		create table %s (
		id integer primary key AUTOINCREMENT,
		termNum text not null,
		lotteryTime  text not null,
		
		''' % tablename
		#print (sqlstr)
		datastr=""
		for i in range(1,11):
			if i!=10:
				datastr+="n%d integer,\n" %(i)
			else:
				datastr+="n%d integer)\n" %(i)
		# print (datastr)
		sqlstr=sqlstr+datastr
		# print (sqlstr)
		con.execute(sqlstr)
	else:
		print("table %s alread existed" %(tablename))



def insertOneRowToDB(conn, tablename, rdata):
    keys = ','.join(rdata.keys())
    question_marks = ','.join(list('?'*len(rdata)))
    values = tuple(rdata.values())
    #print('INSERT INTO '+tablename+' ('+keys+') VALUES ('+question_marks+')')
    conn.execute('INSERT INTO '+tablename+' ('+keys+') VALUES ('+question_marks+')', values)
    conn.commit()




def getonedaydata(date="2017-01-02"):
	url="http://www.cphui.com/pk10/getHistoryData?count=&date="+date+"&t=0.577461605231151"
	global header
	print("getting data from website: %s" %(date))
	while True:
		try:
			http=requests.get(url,headers=headers,timeout=3)
			break;
		except:
			print("timeout")

	if (http.status_code!=200):
		return None
	data=http.content
	lotterydata=json.loads(data)
	if "msg" not in lotterydata:
		# print("*"*20)
		#print(lotterydata["rows"][0])

		daydata=lotterydata["rows"]
		if daydata==None:
			print ("the data is not in this website!")
			return None
		datalen=(len(daydata))
		count=1
		oldterNum=0
		##check data completeity
		# for i in daydata:
		# 	if oldterNum==0:
		# 		oldterNum=int(i["termNum"])
		# 	else:
		# 		if (oldterNum-int(i["termNum"])!=1):
		# 			print (oldterNum)
		# 			break
		# 		else:
		# 			oldterNum=int(i["termNum"])

		# 	print (count,i["termNum"])
		# 	count+=1
		print("datalen is "+str(datalen))
		if datalen<178:
			print("data is not complete")
			return None
		return daydata
	else:
		print("error happened,no valide data")
		return None
def isOnedayDataInDB(conn,tablename,datestr):
	"""
	return value:
	0 :no data in db
	1 : already in db
	-1: data is not complete
	"""
	sqlstr='select count(*) from %s where lotteryTime like "%s' %(tablename, datestr)
	sqlstr+='%";'
	# print (sqlstr)
	resp=conn.execute(sqlstr)
	nums=(resp.fetchone()[0])
	if nums==0:
		return 0 #means no data in db
	elif nums>177:
		return 1 #means data alread in db
	else:
		return -1 #means we have delete the incomplete data and reinsert again


def insertOnedayToDB(conn,tablename,rows):
	"""
	select count(*) from pk10 where lotteryTime like "2017-01-02%";

	"""
	datestr=rows[0]["lotteryTime"][0:10]
	dataSituation=isOnedayDataInDB(conn,tablename,datestr=datestr)
	print (dataSituation)
	if dataSituation==0: #means no data in db
		print ("inserting...")
		for row in rows:
			insertOneRowToDB(conn,tablename,row)
		print ("done!")
	elif dataSituation==1:
		print("the data of %s is already included!" %(datestr))
	else:
		pass #data not complete ,should do delete and insert

def getOnedayDataAndInsert(datestr,conn,tablename):
	dataSituation=isOnedayDataInDB(conn,tablename,datestr=datestr)
	if dataSituation==0: #means no data in db
		rows=getonedaydata(date=datestr)
		if rows:
			for row in rows:
				insertOneRowToDB(conn,tablename,row)
			print ("done!")
	elif dataSituation==1:
		print("the data of %s is already included!" %(datestr))
	else:
		pass #data not complete ,should do delete and insert

if __name__=="__main__":
	DBpath=os.path.abspath("./")
	db=DBpath+"/pk10.db"
	tablename="pk10"
	conn = sqlite3.connect(db)
	createtable(conn,tablename)
	for month in range(1,2):
		monthstr=str(month)
		monthstr=monthstr.zfill(2)
		for day in range(1,31):
			daystr=str(day)
			daystr = daystr.zfill(2)
			date="2017-"+monthstr+"-"+daystr
			getOnedayDataAndInsert(date,conn,tablename)




