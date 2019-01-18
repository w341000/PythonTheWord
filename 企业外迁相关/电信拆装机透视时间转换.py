# -*- coding: utf-8 -*-
import pandas as pd
import datetime
def formatDate(row):
	timestr=row['月份']
	time=datetime.datetime.strptime(timestr, '%Y%m').date()
	tempData=datetime.datetime.strftime(time, "%Y-%m")
	row['月份']=tempData
	return row

filename = 'E:\\svnrepo\\python\\03data\\data\\其他来源\\外迁企业相关\\电信数据\\电信拆装机透视.csv'
with open(filename, "r", encoding='utf-8',newline='') as file:
	df = pd.read_csv(file, dtype=str)
	df.apply(formatDate,axis=1)
	df.to_csv(filename,index=False,sep=',')
