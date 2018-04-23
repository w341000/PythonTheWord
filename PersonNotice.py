# -*- coding: utf-8 -*-
# 对深圳市人力资源和社会保障局的高层次专业人才公式公告爬取数据
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
from pandas import DataFrame, Series
import csv
import os
import win32com, re
from win32com.client import Dispatch, constants
from docx import Document
import urllib
import socket
from urllib import error


# 打开url,如果超时则自旋重试,重试次数太多则放弃并抛出异常
def open_url(url,timeout):
	# socket.setdefaulttimeout(timeout)  # timeout秒内没有打开web页面，就算超时
	self_rotation = 5
	i = 0
	while i<self_rotation:
		try:
			html = urlopen(url,timeout=timeout).read()
			return html
		except: #处理所有异常
			print("从url发生连接错误,尝试重新获取连接")
			i += 1
			continue
	raise RuntimeError('尝试5次连接失败,网络异常!')

# 删除文件
def delete_file(f):
	if os.path.exists(f):
		# 删除文件，可使用以下两种方法。
		os.remove(f)
	else:
		pass


# 获取公告对应的url链接
def get_infourl(url):
	html = open_url(url,20)#20秒超时
	bsObj = BeautifulSoup(html, "html.parser",from_encoding="gb18030")
	liTags = bsObj.find("ul", {"class": "conRight_text_ul1"}).find_all("li")
	add = False
	url_arr = []
	# 获取当前url的目录地址
	offset = url.rfind("/")
	url_prefix = url[:offset + 1]
	# 只获取高层次专业人才认定公式公告
	for liTag in liTags:
		aTag = liTag.find("a")
		title = aTag.attrs["title"]
		if "高层次专业人才认定公示公告" in title:
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


# 解析docx表格中的人才数据
def parse_docx(f, person_info):
	# 读取docx中的表格数据到person_info中
	d = Document(f)
	t = d.tables[0]
	rows = t.rows
	for row in rows[1:]:  # 跳过第一行标题行
		cells = row.cells
		person_info["工作单位"].append(cells[1].text)
		person_info["姓名"].append(cells[2].text)
		person_info["认定级别"].append(cells[3].text)
		person_info["主要认定依据"].append(cells[4].text)


# 下载doc文档并导入到person_info中
def download2person_info(doc_url,person_info):
	temp_doc = 'D:\\011111111111111111111111\\temp\\temp_rencai.doc'
	urllib.request.urlretrieve(doc_url, temp_doc)  # 下载doc文件
	# 将doc文件转为docx文件
	word = win32com.client.Dispatch('Word.Application')
	doc = word.Documents.Open(temp_doc)
	temp_docx_file = 'D:\\011111111111111111111111\\temp\\temp_rencai.docx'
	doc.SaveAs(temp_docx_file, 12, False, "", True, "", False, False, False, False)  # 转化后路径下的文件
	doc.Close()
	word.Quit()
	delete_file(temp_doc)#删除doc文件
	# 从docx文件读取表格信息
	parse_docx(temp_docx_file, person_info)
	delete_file(temp_docx_file)#删除docx文件

# 获取人才数据
def get_person_info(url, person_info):
	html = open_url(url,20)#20秒超时
	bsObj = BeautifulSoup(html, "html.parser",from_encoding="gb18030")
	table_tag = bsObj.find("table")
	if table_tag == None:  # 没有table标签,尝试抓取下载的连接地址并下载doc文件
		main_div = bsObj.find('div', {'class': 'conRight_text2'})
		text = re.search(re.compile("(附件)+"), main_div.get_text())
		if text != None:
			href = main_div.find('div', {'class': 'nr'}).find('a').get('href')
			doc_url = get_docurl(url, href)
			download2person_info(doc_url,person_info)
		else:
			print('该页面没有表格或doc文档')
	else:
		trs = table_tag.find_all("tr")[1:]
		for tr in trs:
			tds = tr.find_all("td")
			person_info["工作单位"].append(tds[1].get_text().strip())
			person_info["姓名"].append(tds[2].get_text().strip())
			person_info["认定级别"].append(tds[3].get_text().strip())
			person_info["主要认定依据"].append(tds[4].get_text().strip())


# 入口函数
def do_search():
	person_info = {"工作单位": [], "姓名": [], "认定级别": [], "主要认定依据": []}
	url_prefix = "http://www.szhrss.gov.cn/ztfw/gccrc/xwgg/gccrc/"  # +index.htm"
	for i in range(24):
		url = ""
		if i == 0:
			url = url_prefix + "index.htm"
		else:
			url = url_prefix + "index_" + str(i) + ".htm"
		print("从url：" + url + "获取所有详细信息地址，当前第" + str(i + 1) + "页")
		url_arr = get_infourl(url)
		for url in url_arr:
			get_person_info(url, person_info)
	table1_df = DataFrame(person_info)
	table1_df.to_csv("D:\\011111111111111111111111\\00临时文件\\personNotice.csv", index=False, sep=',')
	print(table1_df)



# get_person_info("http://www.szhrss.gov.cn/ztfw/gccrc/xwgg/gccrc/201803/t20180323_11632424.htm")
# table1_df = DataFrame(person_info)
# table1_df.to_csv("D:\\011111111111111111111111\\00临时文件\\personNotice.csv", index=False, sep=',')
# print(table1_df)
# url=get_docurl('http://www.szhrss.gov.cn/ztfw/gccrc/xwgg/gccrc/201506/t20150626_2932808.htm','./P020150626566457205987.doc')
# print(url)

do_search()
