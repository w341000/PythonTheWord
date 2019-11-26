# -*- coding: utf-8 -*-
import json
import time
from os import path

from selenium import webdriver

from util import spider_util

browser = webdriver.Chrome()
browser.implicitly_wait(3)

header = {}


def login():
	browser.get("http://10.248.96.106:9517/DataSupport/gotoLogin.xhtml?language=zh_CN")
	username = browser.find_element_by_id('user')
	username.send_keys('admin')
	password = browser.find_element_by_id('pwd')
	password.send_keys('dsp123456')
	browser.find_element_by_css_selector('.button').click()
	# header = {"Cookie": browser.get_cookie('JSESSIONID').get('value'),
	# 		  "Accept": "application/json, text/javascript, */*; q=0.01"
	# 		  }
	time.sleep(3)
	header["Cookie"] = 'JSESSIONID=' + browser.get_cookie('JSESSIONID').get('value')
	header["Accept"] = 'application/json, text/javascript, */*; q=0.01'


def gene_table_sql(api):
	"""
	根据api生成建表语句
	:param api:
	:return:
	"""
	table = api['dataTable']
	url = 'http://10.248.96.106:9517/DataSupport/dataapi/columns.xhtml?tableName=' + table
	data = spider_util.open_url(url, header=header)
	fields = json.loads(data)
	return get_sql(api, fields)


def get_sql(api, field_arr=None):
	if field_arr is None:
		field_arr = []
	table = api["dataTable"]
	table_comments = api["name"]
	sql = ""
	sql = sql + "drop table if exists "+table + " ;\n"
	sql = sql + "create table " + table + "(\n"
	for field in field_arr:
		if field['type']=='CLOB':
			continue
		if field['type']=='BLOB':
			continue
		sql = sql + field["name"] + " varchar(255) comment '" + field["comment"] + "',\n"
	sql=sql[:-2]
	sql = sql + ")DEFAULT CHARSET=utf8 COMMENT='" + table_comments + "';\n"
	return sql


def main():
	interfaces = ['经济运行主题库-商事基本信息', '经济运行主题库-私营主体信息', '经济运行主题库-外资企业信息', '经济运行主题库-证照基本信息',
				  '经济运行主题库-本市生产总值三次产业信息','经济运行主题库-三次产业贡献信息','经济运行主题库-深圳市各行业增加信息','经济运行主题库-各行业增加值构成项目信息',
				  '经济运行主题库-深圳市各区生产总值信息','经济运行主题库-按行业分的社会劳动者人数','经济运行主题库-社会劳动者人数','经济运行主题库-分经济类型和行业城镇单位从业人员']
	login()  # 登陆获取cookie信息
	cookie = browser.get_cookie("JSESSIONID")
	page = 1
	rows = 30
	url = 'http://10.248.96.106:9517/DataSupport/dataapi/apiList.xhtml?page=1&rows=15'
	data = spider_util.open_url(url, self_rotation=60,timeout=60, header=header)
	jsondata = json.loads(data)
	total = jsondata.get('total')

	while True:
		if (page * rows) > int(total):
			break
		print('当前第'+str(page)+'页')
		url = 'http://10.248.96.106:9517/DataSupport/dataapi/apiList.xhtml?page=' + str(page) + '&rows=' + str(rows)
		data = spider_util.open_url(url, self_rotation=60, timeout=60, header=header)
		jsondata = json.loads(data)
		apis = jsondata.get("rows")
		for api in apis:
			if api["name"] in interfaces:
				sql = gene_table_sql(api)
				with open(file=path.join('D:\\011111111111111111111111\\支撑平台建表', api["name"] + '.sql'), mode="w",
						  encoding="utf-8") as file:
					file.write(sql)
					print('生成' + api["name"] + 'sql文件')
		page += 1
	browser.close()


if __name__ == '__main__':
	main()
