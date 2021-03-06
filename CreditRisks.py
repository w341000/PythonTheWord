# -*- coding: utf-8 -*-
# 爬取深圳信用网信用风险相关企业数据
import os
import re
import time
from urllib import error
from urllib import parse, request
from urllib.request import urlopen

from bs4 import BeautifulSoup
from pandas import DataFrame

max_col_length = 10  # 列最大数量


def open_url(req, timeout, self_rotation=10):
	"""
	打开url,如果超时则自旋重试,重试次数太多则放弃并抛出异常
	:param req: request请求对象
	:param timeout: 超时时间
	:param self_rotation: 重试次数
	:return: bsObj文档对象
	"""
	i = 0
	while i < self_rotation:
		try:
			html = urlopen(req, timeout=timeout).read()  # 超时时间
			bsObj = BeautifulSoup(html, "html.parser", from_encoding="gb18030")
			if is_frequently(bsObj):
				print('请求太频繁')
				return None
			return bsObj
		except error.HTTPError as e:
			if i > 1:
				raise e  # 抛出这个http异常,表示该url有问题
			i += 1
			continue
		except Exception as e:
			print("从url发生连接错误,尝试重新获取连接:" + repr(e))
			i += 1
			continue
	return None


def get_values(bsObj, values):
	"""
	从当前文档路径获取访问下一页的地址所需携带的参数
	:param bsObj:
	:param values:
	:return:
	"""
	__VIEWSTATE = bsObj.find('input', {'id': '__VIEWSTATE'})['value']
	__EVENTVALIDATION = bsObj.find('input', {'id': '__EVENTVALIDATION'})['value']
	__VIEWSTATEGENERATOR = bsObj.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
	values['__VIEWSTATE'] = __VIEWSTATE
	values['__EVENTVALIDATION'] = __EVENTVALIDATION
	values['ScriptManager1'] = 'UpdatePanel1|turnPageBar$lbtnNextPage'
	values['__VIEWSTATEGENERATOR'] = __VIEWSTATEGENERATOR
	values['__EVENTTARGET'] = 'turnPageBar$lbtnNextPage'


def get_infourl(bsObj, url_prefix, url_arr=[]):
	"""
	获取每页公司对应的url
	:param bsObj:页面列表的文档对象
	:param url_prefix: url拼接前缀(如果href中的路径为相对路径,则使用前缀拼接)
	:param url_arr: 当前页面的所有公司url列表
	:return:
	"""
	ddTags = bsObj.find_all("dd")
	for ddTag in ddTags:
		href = url_prefix + ddTag.find("a").get("href")
		url_arr.append(href)
	return url_arr


def is_frequently(bsObj):
	"""
	判断是否太过频繁
	:param bsObj: 文档对象
	:return:
	"""
	text = bsObj.getText()
	result = re.search('(您的查询过于频繁)+', text)
	return result is not None


def get_metadata(bsObj):
	"""
	获取元数据信息
	:param bsObj:  文档对象
	:return: 包含元数据的键值对象
	"""
	base_table = bsObj.find("table", {"id": "Table31"})  # 基本信息中除了企业变更以外的其他信息
	tydm_tag = base_table.find('td', text="统一社会信用代码")
	if tydm_tag is None:
		tydm = ''
	else:
		tydm = tydm_tag.find_parent().find_all("td")[-1].get_text().strip()
	qymc_tag = base_table.find('td', text="企业名称")
	if qymc_tag is None:
		qymc_tag = base_table.find('td', text="名称")
	if qymc_tag is None:
		qymc = ''
	else:
		qymc = qymc_tag.find_parent().find_all("td")[-1].get_text().strip();
	zch_tag = base_table.find('td', text="注册号")
	if zch_tag is None:
		zch = ''
	else:
		zch = zch_tag.find_parent().find_all("td")[-1].get_text().strip()
	jgdm_tag = base_table.find('td', text="机构代码")
	if jgdm_tag is None:
		jgdm = ''
	else:
		jgdm = jgdm_tag.find_parent().find_all("td")[-1].get_text().strip()
	sbdwbm_tag = base_table.find('td', text="社保单位编号")
	if sbdwbm_tag is None:
		sbdwbm = ''
	else:
		sbdwbm = sbdwbm_tag.find_parent().find_all("td")[-1].get_text().strip()
	metedata = {"统一社会信用代码": tydm, "企业名称": qymc, "注册号": zch, "机构代码": jgdm, "社保单位编号": sbdwbm}
	return metedata


def get_info(bsObj, base_table, info_table):
	"""
	获取深圳信用网中的公司所有信息
	:param bsObj: 公司页面文档对象
	:param base_table: 保存公司基本信息的对象
	:param info_table: 保存公司提示信息的对象
	:return:
	"""
	metedata = get_metadata(bsObj)
	get_baseinfo(bsObj, base_table, metedata)
	get_promptinfo(bsObj, info_table, metedata)


def get_change_info(bsObj, table, metedata):
	"""
	获取企业变更信息
	:param bsObj: 文档对象
	:param table: 需要保存到的表格
	:param metedata: 企业元数据信息
	:return:
	"""
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
		td_length = len(tds) - 1  # length-1则不获取查看变更信息这一列
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
				pattern = re.compile('(\[.*\])+')
				text = re.sub(pattern, '', text)
				text = text.replace('\n', '')  # 替换换行符
				table[key].append(text)


def do_normal_table(table, normal_tables=[], metedata={}):
	"""
	对不需要反转的表格进行处理
	:param table: 保存到的表格
	:param normal_tables: 信息页面中所有不需要反转处理的表格(如第一列为key头第二列为value)
	:param metedata: 公司原数据信息
	:return:
	"""
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
			if len(tds) > max_col_length:
				print('当前表格列数超过最大列数:' + str(len(tds)) + "列,当前公司:" + metedata['企业名称'] + ',当前分类:' + title)
			for i in range(max_col_length):  # 每一列(单元格)遍历
				key = 'col' + str(i)
				if i >= td_length:
					table[key].append('')
				else:
					td = tds[i]
					text = td.get_text()
					pattern = re.compile('(\[.*\])+')
					text = re.sub(pattern, '', text)
					text = text.replace('\n', '')  # 替换换行符
					table[key].append(text)


def do_reverse_table(table, reverse_tables=[], metedata={}):
	"""
	对需要反转的表格进行处理
	:param table: 保存到的表格
	:param reverse_tables: 所有需要反转处理的表格(如第一行为标题行,其它行为数据行)
	:param metedata: 公司元数据信息
	:return:
	"""
	for reverse_table in reverse_tables:
		title = reverse_table['title']
		time = reverse_table['time']
		trs = reverse_table["table"].find_all("tr")
		field_tr = trs[0]  # 首行为标题行
		comment = ''  # 备注信息
		group = 0  # 分组序号信息
		style = trs[1].find('td').get('style')
		for td in field_tr.find_all('td'):
			if comment == '':
				comment = td.get_text().strip()
			else:
				comment = comment + "-" + td.get_text().strip()
		for tr in trs[1:]:  # 第2行开始是数据行
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
			if len(tds) > max_col_length:
				print('当前表格列数超过最大列数:' + str(len(tds)) + "列,当前公司:" + metedata['企业名称'] + ',当前分类:' + title)
			for i in range(max_col_length):  # 每一列(单元格)遍历
				key = 'col' + str(i)
				if i >= td_length:
					table[key].append('')
				else:
					td = tds[i]
					text = td.get_text()
					pattern = re.compile('(\[.*\])+')
					text = re.sub(pattern, '', text)
					text = text.replace('\n', '')  # 替换换行符
					table[key].append(text)


def get_filter_table(table_info):
	"""
	获取过滤分类后的table信息
	table_info是外层的table,里面包含了如基本信息里的表格数据或提示信息的表格数据(注意,基本信息与提示信息的表格是分开的)
	:param table_info:
	:return:
	"""
	title_trs = table_info.find_all("tr", {"style": "font-weight:bold;"})
	tables = table_info.find_all("table")
	normal_tables = []
	reverse_tables = []
	for i in range(len(title_trs)):  # 对每一个分类信息进行遍历
		title = title_trs[i].find("a", {"class": "sjli"}).get_text().strip()
		time = title_trs[i].find("a", {"class": "sja"}).get_text().strip()
		text = re.search(re.compile("[0-9]+\-[0-9]+\-[0-9]+"), time)
		time = text.group() if text is not None else ''
		table = tables[i]
		table_dict = {"title": title, "time": time, "table": table}
		# 判断该table是否是反转的
		is_reverse = table.find('tr',
								{'style': 'background-color:rgb(243, 243, 243);'}) is not None  # 不等于空则该table是需要被反转的
		if title == '企业年报信息':
			continue
		elif is_reverse:
			reverse_tables.append(table_dict)
		else:
			normal_tables.append(table_dict)
	return {"reverse_tables": reverse_tables, "normal_tables": normal_tables}


# 获取公司信息中的基本信息数据
def get_baseinfo(bsObj, base_table, metedata):
	base_table_tag = bsObj.find("table", {"id": "Table31"})  # 基本信息中除了企业变更以外的其他信息
	filter_table = get_filter_table(base_table_tag)  # 获取过滤后的基本信息中的table
	do_normal_table(base_table, filter_table["normal_tables"], metedata)  # 处理普通table
	do_reverse_table(base_table, filter_table["reverse_tables"], metedata)  # 处理反转table
	get_change_info(bsObj, base_table, metedata)  # 获取企业变更信息


def get_promptinfo(bsObj, info_table, metedata):
	"""
	获取公司信息中的提示信息
	:param bsObj: 文档对象
	:param info_table:提示信息保存到的表格
	:param metedata: 公司元数据信息
	:return:
	"""
	info_table_tag = bsObj.find('table', {'id': 'Table4'})
	if info_table_tag is None:
		return
	filter_table = get_filter_table(info_table_tag)
	do_normal_table(info_table, filter_table["normal_tables"], metedata)  # 处理普通table
	do_reverse_table(info_table, filter_table["reverse_tables"], metedata)  # 处理反转table


def get_all_url_arr(main_url, f, page):
	"""
	获取企业信用风险中的所有公司的url地址,将会首先尝试从文件中读取所有url,如果文件不存在则尝试从网络中获取
	所有链接并返回列表,链接将被写入到文本中以备下次使用
	:param main_url: 获取链接主页面地址
	:param page: 总页数
	:param f: 包含url的文件路径
	:return: 包含所有url的列表
	"""
	if os.path.isfile(f):  # 文件存在
		with open(f, 'r') as file:
			url_arr = []
			for line in file.readlines():
				line = line.strip()  # 把末尾的'\n'删掉
				url_arr.append(line)
			return url_arr
	else:
		headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)', 'Host': 'www.szcredit.org.cn',
				   'Pragma': 'no-cache'
			, 'Referer': 'https://www.szcredit.org.cn/web/GSPT/CreditRiskList.aspx', 'Upgrade-Insecure-Requests': '1'
			, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
			, 'Accept-Language': 'zh-CN,zh;q=0.9'}
		values = {}  # post请求携带的参数
		url_arr = []
		try:
			for i in range(page):
				print('当前第' + str(i + 1) + '页')
				values['turnPageBar$txtPageSize'] = 25
				values['turnPageBar$txtPageNum'] = i
				data = parse.urlencode(values).encode('utf-8')
				req = request.Request(url=main_url, data=data, headers=headers)
				html_obj = open_url(req, 5)
				get_values(html_obj, values)
				get_infourl(html_obj, 'https://www.szcredit.org.cn/web/GSPT/', url_arr)  # 获取每页各个公司对应的url
			# 将获取的url数组存入磁盘
			with open(f, 'w') as file:
				for url in url_arr:
					url = url.strip() + '\n'
					file.write(url)

			return url_arr
		except RuntimeError as e:
			print("获取url地址发生异常")


# 读取已经处理的url
def get_writed_url(f):
	if os.path.isfile(f):  # 文件存在
		with open(f, 'r') as file:
			writed_url = []
			for line in file.readlines():
				line = line.strip()  # 把末尾的'\n'删掉
				writed_url.append(line)

			return writed_url
	else:
		return []


# 写入已经处理的url
def write_writed_url(f, writed_url=[]):
	with open(f, 'w') as file:
		for url in writed_url:
			url = url.strip() + '\n'
			file.write(url)


# 获取错误的url
def get_error_url(f):
	if os.path.isfile(f):  # 文件存在
		with open(f, 'r') as file:
			error_url = []
			for line in file.readlines():
				line = line.strip()  # 把末尾的'\n'删掉
				error_url.append(line)

			return error_url
	else:
		return []


# 写入产生错误的的url,如504等
def write_error_url(f, error_url=[]):
	with open(f, 'w') as file:
		for url in error_url:
			url = url.strip() + '\n'
			file.write(url)


# 企业数据入口函数
def do_search(main_url, page, all_url_file, error_url_file, writed_url_file, base_csv, info_csv):
	headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)', 'Host': 'www.szcredit.org.cn',
			   'Pragma': 'no-cache'
		, 'Referer': 'https://www.szcredit.org.cn/web/GSPT/CreditRiskList.aspx', 'Upgrade-Insecure-Requests': '1'
		, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
		, 'Accept-Language': 'zh-CN,zh;q=0.9'
			   }
	base_table = {'col0': [], 'col1': [], 'col2': [], 'col3': [], 'col4': [], 'col5': [], 'col6': [], 'col7': [],
				  'col8': [], 'col9': [], '所属分类': [],
				  '分组序号': [], '企业名称': [], '注册号': [],
				  '统一社会信用代码': [],
				  '机构代码': [], '社保单位编号': [], '更新时间': [], '备注': [],'爬取时间':[]}  # 存放抓取到的基本信息数据

	info_table = {'col0': [], 'col1': [], 'col2': [], 'col3': [], 'col4': [], 'col5': [], 'col6': [], 'col7': [],
				  'col8': [], 'col9': [], '所属分类': [],
				  '分组序号': [], '企业名称': [], '注册号': [],
				  '统一社会信用代码': [],
				  '机构代码': [], '社保单位编号': [], '更新时间': [], '备注': [],'爬取时间':[]}  # 存放抓取到的提示信息数据
	delay = 15  # 间隔时间
	url_arr = get_all_url_arr(main_url, f=all_url_file, page=page)  # 获取所有url
	writed_url = get_writed_url(writed_url_file)
	error_url = get_error_url(error_url_file)
	print('开始进行数据获取')
	for url in url_arr:
		if url in error_url:  # 该url是发生错误的url
			continue
		if url in writed_url:  # 已经写入的url
			continue
		req = request.Request(url=url, headers=headers)
		try:
			bsObj = open_url(req, 90)
		except error.HTTPError as e:
			print('url:' + url + '请求失败,将该url保存到错误列表中并跳过')
			error_url.append(url)  # 发生了错误的url
			continue
		if bsObj is None:
			print('请求太频繁或建立连接失败,保存现有数据')
			break
		else:
			writed_url.append(url)
			get_info(bsObj, base_table, info_table)  # 数据解析
			time.sleep(delay)  # 间隔时间
	crawl_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	for i in range(len(base_table['更新时间'])):
		base_table['爬取时间'].append(crawl_time)
	for i in range(len(info_table['更新时间'])):
		info_table['爬取时间'].append(crawl_time)
	base_table_df = DataFrame(base_table)
	info_table_df = DataFrame(info_table)
	base_table_df.to_csv(base_csv, mode='a+', index=False, sep=',', header=False)  # 追加模式
	info_table_df.to_csv(info_csv, mode='a+', index=False, sep=',', header=False)  # 追加模式
	write_writed_url(writed_url_file, writed_url)  # 写入已经处理的url
	write_error_url(error_url_file, error_url)  # 写入产生http错误的url


# 企业信用风险数据
def do_credit_risk_list():
	main_url = 'https://www.szcredit.org.cn/web/GSPT/CreditRiskList.aspx'  # 深圳信用网信用风险提示url
	all_url_file = 'd://all_url_arr.txt'
	writed_url_file = 'd://writed_url.txt'  # 保存已经处理的url
	error_url_file = 'd://error_url.txt'
	page = 139
	base_csv = "D:\\011111111111111111111111\\00临时文件\\creaditrisks_base.csv"
	info_csv = "D:\\011111111111111111111111\\00临时文件\\creaditrisks_info.csv"
	do_search(main_url=main_url, page=page, all_url_file=all_url_file, error_url_file=error_url_file,
			  writed_url_file=writed_url_file, base_csv=base_csv, info_csv=info_csv)


# 红名单企业数据
def do_redlist_list():
	main_url = 'https://www.szcredit.org.cn/web/GSPT/RedEntList.aspx'  # 深圳信用网信用风险提示url
	all_url_file = 'd://redlist_all_url_arr.txt'
	writed_url_file = 'd://redlist_writed_url.txt'  # 保存已经处理的url
	error_url_file = 'd://redlist_error_url.txt'
	page = 4
	base_csv = "D:\\011111111111111111111111\\00临时文件\\redlist_base.csv"
	info_csv = "D:\\011111111111111111111111\\00临时文件\\redlist_info.csv"
	do_search(main_url=main_url, page=page, all_url_file=all_url_file, error_url_file=error_url_file,
			  writed_url_file=writed_url_file, base_csv=base_csv, info_csv=info_csv)


# 黑名单企业数据
def do_black_list():
	main_url = 'https://www.szcredit.org.cn/web/GSPT/BlackEntList.aspx'  # 深圳信用网信用风险提示url
	all_url_file = 'd://blacklist_all_url_arr.txt'
	writed_url_file = 'd://blacklist_writed_url.txt'  # 保存已经处理的url
	error_url_file = 'd://blacklist_error_url.txt'
	page = 2110
	base_csv = "D:\\011111111111111111111111\\00临时文件\\blacklist_base.csv"
	info_csv = "D:\\011111111111111111111111\\00临时文件\\blacklist_info.csv"
	do_search(main_url=main_url, page=page, all_url_file=all_url_file, error_url_file=error_url_file,
			  writed_url_file=writed_url_file, base_csv=base_csv, info_csv=info_csv)


if __name__ == "__main__":
	do_black_list()
