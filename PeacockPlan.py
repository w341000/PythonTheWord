# -*- coding: utf-8 -*-
# 爬取人社局中的孔雀计划相关数据
import xlrd

import spider_util
import office_util
from bs4 import BeautifulSoup
from pandas import DataFrame, Series
import re
import urllib


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


def get_xls_url(cur_url, href):
	if re.match(re.compile('^(\./).*$'), href):
		href = href[2:]
	offset = cur_url.rfind("/")
	url_prefix = cur_url[:offset + 1]
	url = url_prefix + href
	return url


def download2person_info(url, data_arr=[],extra=None):
	"""
	下载文档并导入列表中
	:param url:
	:param data_arr:
	:param extra:
	:return:
	"""
	ext = url[url.rfind('.'):]
	temp_file = 'D:\\011111111111111111111111\\temp\\temp_peacocl_paln' + ext
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
				if re.search('姓名', name) is not None:
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
					cell_value=str(row[i]).replace('\n',' ')#过滤换行符号
					app[header_row_values[i]] = cell_value  # 表头与数据对应
				if extra is not None and isinstance(extra, dict):
					for key in extra:
						value = extra[key]
						app[key] = value
				data_arr.append(app)
	spider_util.delete_file(temp_file)  # 删除该文件


def get_info_data(url='', person_info=[]):
	"""
	获取孔雀计划人才数据
	"""
	try:
		html = spider_util.open_url(url, 5, 20)  # 20秒超时
		bsObj = BeautifulSoup(html, "html.parser", from_encoding="gb18030")
		main_div = bsObj.find('div', {'class': 'conRight_text2'})
		title = main_div.find('h4').get_text()
		time_text = main_div.find('p', {
			'style': 'text-align:center; line-height:22px; color:#333;background-color: #efefef;'}).get_text().strip()
		time = re.search('\d{3,4}\-\d{1,2}\-\d{1,2}', time_text).group()
		extra = {'时间': time, '标题': title}
		li_tag = bsObj.find('li')
		href=li_tag.find('a').get('href')
		doc_url = get_xls_url(url, href)
		download2person_info(doc_url, person_info,extra=extra)
	except Exception as e:
		print('获取孔雀计划人才数据失败,原因:%s' % e)


def main():
	peacock_plan = []
	url_prefix = "http://www.szhrss.gov.cn/ztfw/gccrc/xwgg/kqjh/"  # +index.htm"
	for i in range(8):
		if i == 0:
			url = url_prefix + "index.htm"
		else:
			url = url_prefix + "index_" + str(i) + ".htm"
		print("从url：" + url + "获取所有详细信息地址，当前第%s页" % str(i+1))
		url_arr = get_infourl(url,'.*孔雀计划.*批认定人选公示(通告|公告)')
		for url in url_arr:
			get_info_data(url, peacock_plan)

	for i in range(len(peacock_plan)):
		data=peacock_plan[i]
		temp_data={}
		for key in data:
			if re.search('序列|序号', key) is not None:
				continue
			elif re.search('姓名', key) is not None:
				temp_data['姓名'] = data[key]
			elif re.search('学历',key) is not None:
				temp_data['学历']=data[key]
			elif re.search('单位', key) is not None:
				temp_data['单位']=data[key]
			elif  re.search('分类|认定级别', key) is not None:
				temp_data['认定级别']=data[key]
			elif re.search('认定(依据|的标准)', key) is not None:
				temp_data['认定标准']=data[key]
			else:
				temp_data[key]=data[key]
		peacock_plan[i]=temp_data
	table1_df = DataFrame(peacock_plan)
	table1_df.to_csv("D:\\011111111111111111111111\\00临时文件\\peacockPlan.csv", index=False, sep=',')
	print(table1_df)


if __name__ == "__main__":
	main()
