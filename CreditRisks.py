# -*- coding: utf-8 -*-
# 爬取深圳信用网信用风险相关企业数据
from urllib.request import urlopen
from urllib import parse, request
from bs4 import BeautifulSoup
import pandas as pd
from pandas import DataFrame, Series
import re
import time

max_col_length=10#列最大数量

# 对请求参数进行获取
def get_values(bsObj, values):
	__VIEWSTATE = bsObj.find('input', {'id': '__VIEWSTATE'})['value']
	__EVENTVALIDATION = bsObj.find('input', {'id': '__EVENTVALIDATION'})['value']
	__VIEWSTATEGENERATOR = bsObj.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
	values['__VIEWSTATE'] = __VIEWSTATE
	values['__EVENTVALIDATION'] = __EVENTVALIDATION
	values['ScriptManager1'] = 'UpdatePanel1|turnPageBar$lbtnNextPage'
	values['__VIEWSTATEGENERATOR'] =__VIEWSTATEGENERATOR
	values['__EVENTTARGET'] = 'turnPageBar$lbtnNextPage'


# 获取每页公司中的url
def get_infourl(bsObj, url_prefix):
	ddTags = bsObj.find_all("dd")
	url_arr = []
	for ddTag in ddTags:
		href = url_prefix + ddTag.find("a").get("href")
		url_arr.append(href)
	return url_arr


# 判断是否太过频繁
def is_frequently(bsObj):
	lastline = ''
	text = bsObj.getText()
	result = re.search('(您的查询过于频繁)+', text)
	return result != None


# 获取元数据信息
def get_metadata(bsObj):
	base_table = bsObj.find("table", {"id": "Table31"})  # 基本信息中除了企业变更以外的其他信息
	tydm = base_table.find('td', text="统一社会信用代码").find_parent().find_all("td")[-1].get_text().strip()
	qymc_tag = base_table.find('td', text="企业名称")
	if qymc_tag == None:
		qymc_tag = base_table.find('td', text="名称")
	qymc = qymc_tag.find_parent().find_all("td")[-1].get_text().strip();
	zch = base_table.find('td', text="注册号").find_parent().find_all("td")[-1].get_text().strip()
	jgdm_tag = base_table.find('td', text="机构代码")
	if jgdm_tag == None:
		jgdm = ''
	else:
		jgdm = jgdm_tag.find_parent().find_all("td")[-1].get_text().strip()
	sbdwbm_tag = base_table.find('td', text="社保单位编号")
	if sbdwbm_tag == None:
		sbdwbm = ''
	else:
		sbdwbm = sbdwbm_tag.find_parent().find_all("td")[-1].get_text().strip()
	metedata = {"统一社会信用代码": tydm, "企业名称": qymc, "注册号": zch, "机构代码": jgdm, "社保单位编号": sbdwbm}
	return metedata


# 获取公司信息中的信息(入口函数)
def get_info(bsObj, base_table, info_table):
	metedata = get_metadata(bsObj)
	get_baseinfo(bsObj,base_table,metedata)
	get_promptinfo(bsObj, info_table, metedata)


# 获取企业变更信息
def get_change_info(bsObj, table, metedata):
	table_tag = bsObj.find('table', {'id': 'Table123'})
	if table_tag == None:
		return
	fir_trs = table_tag.find_all("tr")
	title_tr = fir_trs[0]
	li_tag = title_tr.find("li")
	title = '企业变更信息'
	time = li_tag.find("a").get_text()
	text = re.search(re.compile("[0-9]+\-[0-9]+\-[0-9]+"), time)
	time = text.group() if text != None else ''  # 过滤时间
	reverse_table = fir_trs[1].find('table')
	trs = reverse_table.find_all("tr")
	field_tr = trs[0]
	comment = ''  # 备注信息
	group = 0  # 分组序号信息
	style = trs[1].find('td').get('style')
	for td in field_tr.find_all('td')[:-1]:
		if comment == '':
			comment = td.get_text().strip()
		else:
			comment = comment + "-" + td.get_text().strip()
	for tr in trs[1:]:
		tds = tr.find_all("td")
		td_length = len(tds) - 1#length-1则不获取查看变更信息这一列
		table['所属分类'].append(title)
		table['更新时间'].append(time)
		table['统一社会信用代码'].append(metedata['统一社会信用代码'])
		table['企业名称'].append(metedata['企业名称'])
		table['注册号'].append(metedata['注册号'])
		table['机构代码'].append(metedata['机构代码'])
		table['社保单位编号'].append(metedata['社保单位编号'])
		table['备注'].append(comment)
		line_style = tr.find('td').get('style')
		if style == line_style:
			pass
		else:
			style = line_style
			group += 1
		table['分组序号'].append(group)
		if len(tds) > max_col_length:
			print('当前表格列数超过最大列数:' + str(len(tds)) + "列,当前公司:" + metedata['企业名称'] + ',当前分类:' + title)
		for i in range(max_col_length):  # 每一列(单元格)遍历
			key = 'col' + str(i)
			if i >= td_length:
				table[key].append('')
			else:
				td = tds[i]
				text = td.get_text()
				table[key].append(text)


# 对不需要反转的表格进行处理
def do_normal_table(table, normal_tables=[], metedata={}):
	for normal_table in normal_tables:
		title = normal_table['title']
		time = normal_table['time']
		trs = normal_table["table"].find_all("tr")
		group = 0
		style = trs[0].find('td').get('style')
		for tr in trs:  # 每一行数据遍历
			tds = tr.find_all("td")
			td_length = len(tds)
			table['所属分类'].append(title)
			table['更新时间'].append(time)
			table['统一社会信用代码'].append(metedata['统一社会信用代码'])
			table['企业名称'].append(metedata['企业名称'])
			table['注册号'].append(metedata['注册号'])
			table['机构代码'].append(metedata['机构代码'])
			table['社保单位编号'].append(metedata['社保单位编号'])
			table['备注'].append('')
			line_style = tr.find('td').get('style')
			if style == line_style:
				pass
			else:
				style = line_style
				group += 1
			table['分组序号'].append(group)
			if len(tds)>max_col_length:
				print('当前表格列数超过最大列数:'+str(len(tds))+"列,当前公司:"+metedata['企业名称']+',当前分类:'+title)
			for i in range(max_col_length):  # 每一列(单元格)遍历
				key = 'col' + str(i)
				if i >= td_length:
					table[key].append('')
				else:
					td = tds[i]
					table[key].append(td.get_text())


# 对需要反转的表格进行处理
def do_reverse_table(table, reverse_tables=[], metedata={}):
	for reverse_table in reverse_tables:
		title = reverse_table['title']
		time = reverse_table['time']
		trs = reverse_table["table"].find_all("tr")
		field_tr = trs[0]#首行为标题行
		comment = ''  # 备注信息
		group = 0  # 分组序号信息
		style = trs[1].find('td').get('style')
		for td in field_tr.find_all('td'):
			if comment == '':
				comment = td.get_text().strip()
			else:
				comment = comment + "-" + td.get_text().strip()
		for tr in trs[1:]:#第2行开始是数据行
			tds = tr.find_all("td")
			td_length = len(tds)
			table['所属分类'].append(title)
			table['更新时间'].append(time)
			table['统一社会信用代码'].append(metedata['统一社会信用代码'])
			table['企业名称'].append(metedata['企业名称'])
			table['注册号'].append(metedata['注册号'])
			table['机构代码'].append(metedata['机构代码'])
			table['社保单位编号'].append(metedata['社保单位编号'])
			table['备注'].append(comment)
			line_style = tr.find('td').get('style')
			if style == line_style:
				pass
			else:
				style = line_style
				group += 1
			table['分组序号'].append(group)
			if len(tds)>max_col_length:
				print('当前表格列数超过最大列数:'+str(len(tds))+"列,当前公司:"+metedata['企业名称']+',当前分类:'+title)
			for i in range(max_col_length):  # 每一列(单元格)遍历
				key = 'col' + str(i)
				if i >= td_length:
					table[key].append('')
				else:
					td = tds[i]
					text = td.get_text()
					pattern = re.compile('(\[.*\])+')
					text = re.sub(pattern, '', text)
					table[key].append(text)


# 获取过滤分类后的table信息
# table_info是外层的table,里面包含了如基本信息里的表格数据或提示信息的表格数据(注意,基本信息与提示信息的表格是分开的)
def get_filter_table(table_info):
	title_trs = table_info.find_all("tr", {"style": "font-weight:bold;"})
	tables = table_info.find_all("table")
	normal_tables = []
	reverse_tables = []
	for i in range(len(title_trs)):  # 对每一个分类信息进行遍历
		title = title_trs[i].find("a", {"class": "sjli"}).get_text().strip()
		time = title_trs[i].find("a", {"class": "sja"}).get_text().strip()
		text = re.search(re.compile("[0-9]+\-[0-9]+\-[0-9]+"), time)
		time = text.group() if text != None else ''
		table = tables[i]
		table_dict = {"title": title, "time": time, "table": table}
		#判断该table是否是反转的
		is_reverse=table.find('tr',{'style':'background-color:rgb(243, 243, 243);'})!=None#不等于空则该table是需要被反转的
		if title == '企业年报信息':
			continue
		elif is_reverse:
			reverse_tables.append(table_dict)
		else:
			normal_tables.append(table_dict)
	return {"reverse_tables": reverse_tables, "normal_tables": normal_tables}


#获取公司信息中的基本信息数据
def get_baseinfo(bsObj,base_table,metedata):
	base_table_tag = bsObj.find("table", {"id": "Table31"})  # 基本信息中除了企业变更以外的其他信息
	filter_table = get_filter_table(base_table_tag)  # 获取过滤后的基本信息中的table
	do_normal_table(base_table, filter_table["normal_tables"], metedata)#处理普通table
	do_reverse_table(base_table, filter_table["reverse_tables"], metedata)#处理反转table
	get_change_info(bsObj, base_table, metedata)  # 获取企业变更信息


# 获取公司信息中的提示信息
def get_promptinfo(bsObj, info_table=[], metedata={}):
	info_table_tag = bsObj.find('table', {'id': 'Table4'})
	if info_table_tag == None:
		return
	filter_table = get_filter_table(info_table_tag)
	do_normal_table(info_table, filter_table["normal_tables"], metedata)  # 处理普通table
	do_reverse_table(info_table, filter_table["reverse_tables"], metedata)  # 处理反转table



def do_search():
	headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
	#深圳信用网信用风险提示url
	main_url = 'https://www.szcredit.org.cn/web/GSPT/CreditRiskList.aspx'
	values = {}  # post请求携带的参数
	base_table = {'col0': [], 'col1': [], 'col2': [], 'col3': [], 'col4': [], 'col5': [], 'col6': [],'col7': [],
				  'col8': [],'col9': [],'所属分类': [],
				  '分组序号': [], '企业名称': [], '注册号': [],
				  '统一社会信用代码': [],
				  '机构代码': [], '社保单位编号': [], '更新时间': [], '备注': []}  # 存放抓取到的基本信息数据

	info_table = base_table.copy()  # 存放抓取到的提示信息数据
	for i in range(139):
		print('当前第' + str(i+1) + '页')
		values['turnPageBar$txtPageSize'] = 25
		values['turnPageBar$txtPageNum'] = i
		data = parse.urlencode(values).encode('utf-8')
		req = request.Request(url=main_url, data=data, headers=headers)
		html = request.urlopen(req)
		html_obj = BeautifulSoup(html, "html.parser", from_encoding="gb18030")
		if is_frequently(html_obj):
			print("查询太频繁:当前第"+ str(i) + "页,睡眠1小时")
			time.sleep(3600)
		get_values(html_obj, values)
		url_arr = get_infourl(html_obj, 'https://www.szcredit.org.cn/web/GSPT/')  # 获取每页各个公司对应的url
		i=0
		while i <len(url_arr):
			url=url_arr[i]
			req = request.Request(url=url, headers=headers)
			html = urlopen(req)
			bsObj = BeautifulSoup(html, "html.parser", from_encoding="gb18030")
			if is_frequently(bsObj):
				print("查询太频繁,睡眠1小时")
				time.sleep(3600)
				continue
			get_info(bsObj, base_table, info_table)#数据解析
			time.sleep(11)#间隔11秒
			i+=1
	base_table_df = DataFrame(base_table)
	info_table_df = DataFrame(info_table)
	base_table_df.to_csv("D:\\011111111111111111111111\\00临时文件\\creaditrisks_base.csv", index=False, sep=',')
	info_table_df.to_csv("D:\\011111111111111111111111\\00临时文件\\creaditrisks_info.csv", index=False, sep=',')



def test():
	base_table = {'col0': [], 'col1': [], 'col2': [], 'col3': [], 'col4': [], 'col5': [], 'col6': [],'col7': [],
				  'col8': [],'col9': [], '所属分类': [],'分组序号': [], '企业名称': [], '注册号': [],'统一社会信用代码': [],
				  '机构代码': [], '社保单位编号': [], '更新时间': [], '备注': []}  # 存放抓取到的基本信息数据
	info_table=base_table.copy()# 存放抓取到的提示信息数据
	headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
	url = 'https://www.szcredit.org.cn/web/GSPT/newGSPTDetail3.aspx?ID=3d0ae40633ff41edae1c38baa0b02307'
	req = request.Request(url=url, headers=headers)
	html = urlopen(req)
	bsObj = BeautifulSoup(html, "html.parser", from_encoding="gb18030")
	if is_frequently(bsObj):
		print("查询太频繁")
	get_info(bsObj, base_table, info_table)

	base_table_df = DataFrame(base_table)
	info_table_df = DataFrame(info_table)
	base_table_df.to_csv("D:\\011111111111111111111111\\00临时文件\\creaditrisks_base.csv", index=False, sep=',')
	info_table_df.to_csv("D:\\011111111111111111111111\\00临时文件\\creaditrisks_info.csv", index=False, sep=',')


do_search()
