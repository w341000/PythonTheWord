# -*- coding: utf-8 -*-
import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup
from pandas import DataFrame,Series


# 获得重点企业股票代码

def get_code(path):
	df = pd.read_excel(path, header=None, names=['name', 'code', 'homepage'])
	df = df[df['code'].notnull()]  # 股票代码非空的记录
	df[['code']] = df[['code']].applymap(lambda x: "%.0f" % x)  # 去掉小数
	df[['code']] = df[['code']].applymap(lambda x: x.rjust(6, '0'))  # 6位字符串，不足前面补0
	code_list = df['code']
	return (code_list)


# 从给定url找到新闻公告的内容
def get_dataframe(url):
	html = urlopen(url)
	bsObj = BeautifulSoup(html, "lxml")
	content=bsObj.find("div",{"id":"newsTabs"}).find("div",{"class":"inner_box"})
	return content.get_text()


url_prefix = "http://quotes.money.163.com/f10/gsgg_"
url_suffix = ",zjgg,"
page = 0
ext = ".html"
code_list = get_code("E:\\1000enterprise_code.xlsx")

# 根据股票代码生成所有新闻公告url
for code in code_list:
	url = url_prefix + code + url_suffix +hex(page) + ext
	print(url)
	html = urlopen(url)
	bsObj = BeautifulSoup(html, "lxml")

content=get_dataframe("http://quotes.money.163.com/f10/ggmx_002926_4093447.html")
print(content)
table={"text":[content]}
# table1_df = DataFrame(table)
# print(table1_df)