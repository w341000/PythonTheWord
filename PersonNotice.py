# -*- coding: utf-8 -*-
# 对深圳市人力资源和社会保障局的高层次专业人才公式公告爬取数据
import re
import time
import urllib
from urllib.request import urlopen

import xlrd
from bs4 import BeautifulSoup
from pandas import DataFrame

from util import spider_util, office_util


def get_infourl(url, pattern):
	"""
	获取公告对应的url链接
	:param url: 当前页面的链接地址
	:param pattern: 需要进行比较的正则表达式或正则表达式对象
	:param keyword: 标题中的关键字,只有含有关键字的链接才会被返回
	:return:
	"""
	html = spider_util.open_url(url, 5, 20)  # 20秒超时
	bsObj = BeautifulSoup(html, "html.parser", from_encoding="gb18030")
	liTags = bsObj.find("ul", {"class": "conRight_text_ul1"}).find_all("li")
	url_arr = []
	# 获取当前url的目录地址
	offset = url.rfind("/")
	url_prefix = url[:offset + 1]
	# 只获取高层次专业人才认定公式公告
	for liTag in liTags:
		aTag = liTag.find("a")
		title = aTag.attrs["title"]
		if re.search(pattern, string=title) is not None:
			href = url_prefix + aTag.attrs["href"][2:]
			url_arr.append(href)
	return url_arr


# 获取doc文档的路径地址
def get_docurl(cur_url, href):
	if re.match(re.compile('^(\./).*$'), href):
		href = href[2:]
	offset = cur_url.rfind("/")
	url_prefix = cur_url[:offset + 1]
	url = url_prefix + href
	return url


def download_to_data_arr(doc_url, data_arr, extra=None):
	"""
	下载office文档读取其中的table并导入到数据列表中中
	:param doc_url: 文档地址
	:param data_arr: 需要保存的数据数组
	:param extra: 需要添加的额外数据
	:return:
	"""
	ext = doc_url[doc_url.rfind('.'):]
	temp_file = 'D:\\011111111111111111111111\\temp\\temp_rencai' + ext
	urllib.request.urlretrieve(doc_url, temp_file)  # 下载word文件
	if ext == '.doc' or ext == '.docx':
		# 从word文件读取表格信息
		office_util.word_table_to_list(temp_file, data_arr, extra=extra)
	elif ext == '.xls' or ext == '.xlsx':
		office_util.excel_table_byname(temp_file, data_arr=data_arr, extra=extra)
	spider_util.delete_file(temp_file)  # 删除该文件


def download_assessment_to_arr(url, data_arr, extra=None):
	"""
	下载人才评估文档并导入列表中
	:param url:
	:param data_arr:
	:param extra:
	:return:
	"""
	ext = url[url.rfind('.'):]
	temp_file = 'D:\\011111111111111111111111\\temp\\temp_rencai' + ext
	urllib.request.urlretrieve(url, temp_file)  # 下载word文件
	if ext == '.doc' or ext == '.docx':
		raise RuntimeError('该文档为不支持的文档类型:%s' % ext)
	elif ext == '.xls' or ext == '.xlsx':
		data = data = xlrd.open_workbook(temp_file)
		table = data.sheet_by_index(0)  # 获得表格
		nrows = table.nrows  # 拿到总共行数
		header_row_index = None
		for i in range(nrows):  # 根据姓名字段判断该行是否为表头行
			colnames = table.row_values(i)
			for name in colnames:
				if name == '姓名':
					header_row_index = i
					break
			if header_row_index is not None:
				break
		header_row_values = table.row_values(header_row_index)
		for rownum in range(header_row_index + 1, nrows):  # 也就是从Excel第二行开始，第一行表头不算
			row = table.row_values(rownum)
			if row:
				app = {}
				for i in range(len(header_row_values)):
					app[header_row_values[i]] = row[i]  # 表头与数据对应
				if extra is not None and isinstance(extra, dict):
					for key in extra:
						value = extra[key]
						app[key] = value
				data_arr.append(app)
	spider_util.delete_file(temp_file)  # 删除该文件


def get_person_info(url, person_info):
	"""
	获取人才数据
	:param url: 人才详情页面地址
	:param person_info:  保存人才信息数据的列表,列表的每个元素为表格每行对应表头的字典
	:return:
	"""
	html = spider_util.open_url(url, self_rotation=5, timeout=20)  # 20秒超时
	bsObj = BeautifulSoup(html, "html.parser", from_encoding="gb18030")
	main_div = bsObj.find('div', {'class': 'conRight_text2'})
	title = main_div.find('h4').get_text()
	content = re.search('（.*）', title)
	# issues 期数
	if content is not None:
		issues = re.search('\d+', content.group()).group()
	else:
		issues = title[title.find('公告') + 2:]
		issues = spider_util.chinese2digits(issues)
	time_text = main_div.find('p', {
		'style': 'text-align:center; line-height:22px; color:#333;background-color: #efefef;'}).get_text().strip()
	table_tag = bsObj.find("table")
	release_time = re.search('\d{3,4}\-\d{1,2}\-\d{1,2}', time_text).group()
	crawl_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	extra = {'期数': issues, '发布时间': release_time, '标题': title, '爬取时间': crawl_time}
	if table_tag is None:  # 没有table标签,尝试抓取下载的连接地址并下载doc文件
		text = re.search(re.compile("(附件)+"), main_div.get_text())
		if text is not None:
			href = main_div.find('div', {'class': 'nr'}).find('li').find('a').get('href')
			doc_url = get_docurl(url, href)
			download_to_data_arr(doc_url, person_info, extra=extra)
		else:
			print('该页面没有表格或doc文档')
	else:
		header_tds = table_tag.find_all("tr")[0].find_all('td')
		trs = table_tag.find_all("tr")[1:]
		for tr in trs:
			tds = tr.find_all("td")
			data = {}
			for i in range(len(tds)):
				field = header_tds[i].get_text().strip()
				field = re.sub('\s+', '', field)  # 替换空格为空
				text = tds[i].get_text().strip()
				data[field] = text
			for key in extra:  # 添加额外数据
				data[key] = extra[key]
			person_info.append(data)


def get_reward(url, data_arr):
	"""
	获取奖励补贴数据
	:param url:
	:param data_arr: 需要保存的数据列表
	:return:
	"""
	html = spider_util.open_url(url, self_rotation=5, timeout=20)  # 20秒超时
	bsObj = BeautifulSoup(html, "html.parser", from_encoding="gb18030")
	main_div = bsObj.find('div', {'class': 'conRight_text2'})
	title = main_div.find('h4').get_text()
	content = re.search('（.*）', title)
	# issues 期数
	if content is not None:
		issues = content.group()[1:-1]  # 跳过括号
	else:
		issues = ''
	time_text = main_div.find('p', {
		'style': 'text-align:center; line-height:22px; color:#333;background-color: #efefef;'}).get_text().strip()
	table_tag = bsObj.find("table")
	release_time = re.search('\d{3,4}\-\d{1,2}\-\d{1,2}', time_text).group()
	crawl_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	extra = {'期数': issues, '发布时间': release_time, '标题': title, '爬取时间': crawl_time}
	if table_tag is None:  # 没有table标签,尝试抓取下载的连接地址并下载doc文件
		text = re.search(re.compile("(附件)+"), main_div.get_text())
		if text is not None:
			href = main_div.find('div', {'class': 'nr'}).find('li').find('a').get('href')
			doc_url = get_docurl(url, href)
			download_to_data_arr(doc_url, data_arr, extra=extra)
		else:
			print('该页面没有表格或文档')
	else:
		header_tds = table_tag.find_all("tr")[0].find_all('td')
		trs = table_tag.find_all("tr")[1:]
		for tr in trs:
			tds = tr.find_all("td")
			data = {}
			for i in range(len(tds)):
				field = header_tds[i].get_text().strip()
				field = re.sub('\s+', '', field)  # 替换空格为空
				text = tds[i].get_text().strip()
				data[field] = text
			for key in extra:  # 添加额外数据
				data[key] = extra[key]
			data_arr.append(data)


def get_assessment(url, data_arr):
	"""
	获取人才评估结果名单
	:param url:
	:param data_arr: 需要保存的数据列表
	:return:
	"""
	html = spider_util.open_url(url, self_rotation=5, timeout=20)  # 20秒超时
	bsObj = BeautifulSoup(html, "html.parser", from_encoding="gb18030")
	main_div = bsObj.find('div', {'class': 'conRight_text2'})
	title = main_div.find('h4').get_text()
	content = re.search('（.*）|\(.*\)', title)
	# issues 期数
	if content is not None:
		issues = content.group()[1:-1]  # 跳过括号
	else:
		issues = ''
	time_text = main_div.find('p', {
		'style': 'text-align:center; line-height:22px; color:#333;background-color: #efefef;'}).get_text().strip()
	release_time = re.search('\d{3,4}\-\d{1,2}\-\d{1,2}', time_text).group()
	crawl_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	extra = {'期数': issues, '发布时间': release_time, '标题': title,'爬取时间':crawl_time}
	# 没有table标签,尝试抓取下载的连接地址并下载doc文件
	text = re.search(re.compile("(附件)+"), main_div.get_text())
	if text is not None:
		li_tags = main_div.find('div', {'class': 'nr'}).find_all('li')
		for li_tag in li_tags:
			a_tag = li_tag.find('a')
			if a_tag is None:
				continue
			href = a_tag.get('href')
			doc_url = get_docurl(url, href)
			download_assessment_to_arr(doc_url, data_arr, extra=extra)
	else:
		print('该页面没有文档')


# 入口函数
def do_search(page=24):
	person_info = []  # 高层次专业人才
	person_reward = []  # 高层次人才奖励补贴人员
	person_assessment = []  # 高层次人才评估结果
	url_prefix = "http://www.szhrss.gov.cn/ztfw/gccrc/xwgg/gccrc/"  # +index.htm"
	for i in range(page):
		url = ""
		if i == 0:
			url = url_prefix + "index.htm"
		else:
			url = url_prefix + "index_" + str(i) + ".htm"
		print("从url：" + url + "获取所有详细信息地址，当前第" + str(i + 1) + "页")
		url_arr = get_infourl(url, "高层次专业人才认定公示公告")
		for url_notice in url_arr:
			get_person_info(url_notice, person_info)
		reward_url_arr = get_infourl(url, "高层次人才奖励补贴拟发放人员名单公示公告")
		for url_reward in reward_url_arr:
			get_reward(url_reward, person_reward)
		assessment_url_arr = get_infourl(url, '.*高层次专业人才.*评估.*公示')
		for assessment_url in assessment_url_arr:
			get_assessment(assessment_url, person_assessment)
	for data in person_info:  # 删除所有序号
		if data.get('序号'):
			data.pop('序号')
	for i in range(len(person_assessment)):  # 删除所有序号
		data = person_assessment[i]
		temp_data = {}
		for key in data:  # 循环时删除元素将产生问题,所有使用复制对象的方法避免
			if key == '序号':
				continue
			elif '级别' in key:
				temp_data['人才级别'] = data[key]
				continue
			else:
				temp_data[key] = data[key]
		person_assessment[i] = temp_data
	for i in range(len(person_reward)):
		data = person_reward[i]
		temp_data = {}
		for key in data:  # 循环时删除元素将产生问题,所有使用复制对象的方法避免
			if key == '序号':
				continue
			elif '级别' in key:
				temp_data['级别'] = data[key]
				continue
			else:
				temp_data[key] = data[key]
		person_reward[i] = temp_data
	DataFrame(person_info).to_csv("D:\\011111111111111111111111\\00临时文件\\personNotice.csv", index=False, sep=',')
	DataFrame(person_reward).to_csv("D:\\011111111111111111111111\\00临时文件\\personNotice_reward.csv", index=False,
									sep=',')
	DataFrame(person_assessment).to_csv("D:\\011111111111111111111111\\00临时文件\\personNotice_assessment.csv",
										index=False,
										sep=',')


if __name__ == "__main__":
	do_search()
	# print('123\n456'.replace('\n',''))
