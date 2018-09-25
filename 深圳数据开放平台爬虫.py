# -*- coding: utf-8 -*-
import pinyin_util
import re
from urllib import error
from bs4 import BeautifulSoup
from pandas import DataFrame

import spider_util






def getField_sql(url):
	"""
	从深圳公开数据平台抓取对应页面字段信息
	:param url:
	:return:获取的字段数组
	"""
	html = spider_util.open_url(url, 5, 20)  # 20秒超时
	bsObj = BeautifulSoup(html, "html.parser", from_encoding="UTF-8")
	title = bsObj.select_one("div.row.operation-headline").get_text().strip()
	title=title.replace(".","点")
	table=bsObj.select("#apicontent table")[1]
	tr_tags=table.select("tr")[2:]
	field_arr=[]
	for tr_tag in tr_tags:
		td_tags=tr_tag.select("td")
		field=td_tags[0].get_text().strip()
		comment=td_tags[2].get_text().strip()
		field_arr.append({"field":field,"comment":comment})
	sql=get_sql(title,field_arr)
	return sql



def get_sql(title,field_arr=[]):
	table=pinyin_util.PinYin().hanzi2pinyin_split(title, "", True).upper()
	table="T_OPEN_"+table
	sql=""
	sql=sql+"drop table "+table+";\n"
	sql=sql+"create table "+table+"(\nRECORDID NUMBER(20),\n"
	for field in field_arr:
		sql=sql+field["field"]+" varchar2(200), \n"
	sql=sql+"WRITETIME date DEFAULT SYSDATE); \n"
	for field in field_arr:
		sql=sql+"COMMENT ON COLUMN 	"+table+" .	"+field["field"]+"	is	'"+field["comment"]+"';\n"
	sql=sql+"COMMENT ON TABLE	"+table+"  	is	'开放平台-"+title+"';\n"
	sql=(sql+"alter table "+table+" add constraint "+table+"_PK primary key (RECORDID) using index;\n"+
			"CREATE OR REPLACE TRIGGER "+table+"_TG  BEFORE INSERT ON "+table+"    FOR EACH ROW  WHEN (new.RECORDID is null) \n"
			"begin \n  select FT_sequence.nextval into :new.RECORDID from dual; \nend; \n \n \n")
	return sql
#field_arr=getField_sql("http://opendata.sz.gov.cn/dataapi/toApiDetail/854/1")
urls=["http://opendata.sz.gov.cn/dataapi/toApiDetail/198/1","http://opendata.sz.gov.cn/dataapi/toApiDetail/348/1",
	  "http://opendata.sz.gov.cn/dataapi/toApiDetail/291/1","http://opendata.sz.gov.cn/dataapi/toApiDetail/3099/1","http://opendata.sz.gov.cn/dataapi/toApiDetail/845/1",
	  "http://opendata.sz.gov.cn/dataapi/toApiDetail/265/1","http://opendata.sz.gov.cn/dataapi/toApiDetail/239/1","http://opendata.sz.gov.cn/dataapi/toApiDetail/344/1",
	  "http://opendata.sz.gov.cn/dataapi/toApiDetail/854/1"]
with open("D:\\opendata.sql","w+") as file:
	for url in urls:
		sql=getField_sql(url)
		file.write(sql)