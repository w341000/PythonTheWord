# -*- coding: utf-8 -*-
#对深圳市人力资源和社会保障局的高层次专业人才公式公告爬取数据
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
from pandas import DataFrame, Series
import re
import csv

def get_infourl(url):
	html = urlopen(url)
	bsObj = BeautifulSoup(html, "html.parser")
	liTags = bsObj.find("ul",{"class":"conRight_text_ul1"}).find_all("li")
	add = False
	url_arr = []
	# 获取当前url的目录地址
	offset = url.rfind("/")
	url_prefix = url[:offset + 1]
	# 只获取高层次专业人才认定公式公告
	for liTag in liTags:
		aTag=liTag.find("a")
		title=aTag.attrs["title"]
		if "高层次专业人才认定公示公告" in title:
			href = url_prefix +aTag.attrs["href"][2:]
			url_arr.append(href)
	return url_arr

person_info={}
person_info["工作单位"]=[]
person_info["姓名"]=[]
person_info["认定级别"]=[]
person_info["主要认定依据"]=[]

def get_person_info(url):
	html = urlopen(url)
	bsObj = BeautifulSoup(html, "html.parser")
	trs=bsObj.find("table").find_all("tr")[1:]
	for tr in trs:
		tds=tr.find_all("td")
		person_info["工作单位"].append(tds[1].get_text().strip())
		person_info["姓名"].append(tds[2].get_text().strip())
		person_info["认定级别"].append(tds[3].get_text().strip())
		person_info["主要认定依据"].append(tds[4].get_text().strip())








url_prefix = "http://www.szhrss.gov.cn/ztfw/gccrc/xwgg/gccrc/"#+index.htm"
table_dict = {}
for i in range(24):
	url=""
	if i==0:
		url=url_prefix+"index.htm"
	else:
		url=url_prefix+"index_"+str(i)+".htm"
	print("从url：" + url + "获取所有详细信息地址，当前第" + str(i + 1) + "页")
	url_arr = get_infourl(url)
	for url in url_arr:
		get_person_info(url)

#get_person_info("http://www.szhrss.gov.cn/ztfw/gccrc/xwgg/gccrc/201803/t20180323_11632424.htm")
# table1_df = DataFrame(person_info)
# table1_df.to_csv("D:\\011111111111111111111111\\00临时文件\\personNotice.csv", index=False, sep=',')
# print(table1_df)
