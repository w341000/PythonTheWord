# -*- coding: utf-8 -*-
import  spider_util
import bs4
from bs4 import BeautifulSoup
import json
import pandas
from pandas import DataFrame
healthIndex=[]
#去掉空格
def strip_blacnk(dataItem={}):
	for key in dataItem.keys():
		value=str(dataItem[key]).strip()
		if key=='street':
			value=value[:-2]
		dataItem[key]=value

#爬取街道卫生指数信息
for year in range(2017,2019):
	for month in range(1,13):
		month=str(month)
		month = month.zfill(2)
		url='http://wnl.52mlsz.com/wx/api/street/healthIndex'
		time=str(year)+'-'+month
		data={'evaluation_time':time,'area_id':1,'rows':200}
		html=spider_util.open_url(url,data=data)
		obj=json.loads(html)
		list=obj['data']['list']
		for dataItem in list:
			dataItem['time']=time
			strip_blacnk(dataItem)
			healthIndex.append(dataItem)

progressIndex=[]
#爬取街道进步指数信息
for year in range(2017,2019):
	for month in range(1,13):
		month=str(month)
		month = month.zfill(2)
		url='http://wnl.52mlsz.com/wx/api/street/progressIndex'
		time=str(year)+'-'+month
		data={'evaluation_time':time,'area_id':1,'rows':200}
		html=spider_util.open_url(url,data=data)
		obj=json.loads(html)
		list=obj['data']['list']
		for dataItem in list:
			dataItem['time']=time
			strip_blacnk(dataItem)
			progressIndex.append(dataItem)





DataFrame(healthIndex).to_csv("D:\\healthIndex.csv",
										index=False,
										sep=',')

DataFrame(progressIndex).to_csv("D:\\progressIndex.csv",
										index=False,
										sep=',')