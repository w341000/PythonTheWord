# -*- coding: utf-8 -*-
# 爬虫工具类
import csv
import os
import re
import socket
import urllib
from urllib import error
from urllib import request
from urllib.request import urlopen

import numpy as np
from bs4 import BeautifulSoup


def open_url(url, self_rotation=5, timeout=5, data=None, header={}) -> BeautifulSoup:
	"""
	打开url,如果超时则自旋重试,重试次数太多则放弃并抛出异常
	:param header:请求头
	:param data: 携带参数,为字典对象如{k:v}
	:param url: 要打开的url地址
	:param self_rotation: 自旋次数
	:param timeout: 超时时间(秒)
	:return:
	:raise RuntimeError: 失败次数超过允许的自旋重试次数,则抛出此异常
	"""
	i = 0
	if data is not None:
		data = bytes(urllib.parse.urlencode(data), encoding='utf8')
	while i < self_rotation:
		try:
			request = urllib.request.Request(url, data, header)
			html = urlopen(request, timeout=timeout).read()
			return html
		except error.HTTPError as e:
			if e.code == 500:
				print("服务器返回500错误,url:" + url)
				raise e
			if e.code == 404:
				print("服务器返回404错误,url:" + url)
				raise e
			else:
				i += 1
				continue
		except Exception as e:
			print("从url发生连接错误,尝试重新获取连接:" + repr(e))
			i += 1
			continue
	print('发生错误,url:' + url)
	print(data)
	raise RuntimeError('尝试%d次连接失败,网络异常!' % self_rotation)


def open_url_return_bsobj(url, self_rotation=5, timeout=5, data=None, from_encoding="utf-8"):
	"""
	打开url,如果超时则自旋重试,重试次数太多则放弃并抛出异常，返回BeautifulSoup文档对象，
	该方法相当于直接调用open_url并调用BeautifulSoup(data, "html.parser", from_encoding="utf-8")
	:param from_encoding: 编码
	:param data: 携带参数,为字典对象如{k:v}
	:param url: 要打开的url地址
	:param self_rotation: 自旋次数
	:param timeout: 超时时间
	:return: BeautifulSoup文档对象
	:raise RuntimeError: 失败次数超过允许的自旋重试次数,则抛出此异常
	"""
	data = open_url(url, self_rotation=self_rotation, timeout=timeout, data=data)
	bsObj = BeautifulSoup(data, "html.parser", from_encoding=from_encoding)
	return bsObj


def delete_file(f):
	"""
	删除文件,文件不存在则忽略
	:param f: 需要被删除的文件
	:return:
	"""
	if os.path.exists(f):
		# 删除文件，可使用以下两种方法。
		os.remove(f)
	else:
		pass


def list_to_file(f='file.txt', arr=[], mode='w'):
	"""
	将arr中的数据按行写入到磁盘文件中
	:param f: 需要被写入的文件
	:param arr:写入文件的数组,数组中的每个元素将被调用str函数进行输出写入文件中
	:param mode:打开文件的模式,默认为覆盖写入
	:return:
	"""
	with open(f, mode) as file:
		for obj in arr:
			line = str(obj) + '\n'
			file.write(line)


def file_to_list(f=''):
	"""
	按行读取文本文件,将文本文件转为数组返回
	:param f: 文件路径
	:return: 包含所有文本的数组,如果文本不存在则返回空数组
	"""
	if os.path.isfile(f):  # 文件存在
		with open(f, 'r') as file:
			text_arr = []
			for line in file.readlines():
				line = line.strip()  # 把末尾的'\n'删掉
				text_arr.append(line)

			return text_arr
	else:
		return []


def get_docurl(cur_url, href):
	"""
	获取href标签的url绝对地址
	:param cur_url:当前页面的路径
	:param href: href中的链接
	:return: 绝对路径
	"""
	if re.match(re.compile('^(\./).*$'), href):
		href = href[2:]
	offset = cur_url.rfind("/")
	url_prefix = cur_url[:offset + 1]
	url = url_prefix + href
	return url


def chinese2digits(uchars_chinese):
	"""
	中文数字转换为阿拉伯数字
	:param uchars_chinese:
	:return: 阿拉伯数字
	"""
	common_used_numerals_tmp = {'零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
								'十': 10, '百': 100, '千': 1000, '万': 10000, '亿': 100000000}
	total = 0
	r = 1  # 表示单位：个十百千...
	for i in range(len(uchars_chinese) - 1, -1, -1):
		val = common_used_numerals_tmp.get(uchars_chinese[i])
		if val >= 10 and i == 0:  # 应对 十三 十四 十*之类
			if val > r:
				r = val
				total = total + val
			else:
				r = r * val
		elif val >= 10:
			if val > r:
				r = val
			else:
				r = r * val
		else:
			total = total + r * val
	return total


# csv文件转换为列表
def readCSV2List(filePath, encoding='utf-8'):
	"""
	csv文件转换为列表信息,返回包含列表及标题的元组
	table_list中以列表形式保存csv文件的值
	:param filePath:文件地址
	:return:(table_list, csvHead)
	"""
	with open(filePath, newline='', encoding=encoding) as csvfile:  # 此方法:当文件不用时会自动关闭文件
		csvReader = csv.DictReader(csvfile)
		reader = csv.reader(csvfile)
		csvHead = csvReader.fieldnames
		print(csvHead)
		table_list = []
		for content in csvReader:
			data = {}
			for head in csvHead:
				data[head] = content[head]
			table_list.append(data)
		return table_list, csvHead


# 输入：文件名称，数据列表
def createListCSV(path="", table_list=[], head=[]):
	"""
	列表转为csv文件
	:param fileName: 文件名称
	:param table_list: 列表数据
	:param head: 表头信息
	:return:
	"""
	with open(path, "w", encoding='utf-8', newline='') as csvFile:
		csvWriter = csv.writer(csvFile)

		# 先写入标题
		csvWriter.writerow(head)
		for table in table_list:
			data = []
			for field in head:
				data.append(table[field])
			csvWriter.writerow(data)
		csvFile.close()


def log_progress(i: int, length: int, start_from_zero=True, detailedLog=False):
	"""
	日志打印记录当前进度

	:param i: 当前位置
	:param length: 总长度
	:param start_from_zero: 值是否从0开始,默认为True  True:  计算进度时，i将会+1再做计算 False:不做修改
	:param detailedLog: 是否打印详细日志，默认为False 当值为False:只有进度为整数百分比 如 2%时才打印，值为True则都打印
	"""
	np.set_printoptions(suppress=True)
	if start_from_zero:
		i += 1
	progress = round(i / length, 5) * 100
	if not detailedLog:
		if not progress == int(progress):
			return
	print('已完成进度：%.5f%%' % progress)


def download(url, filename: str, self_rotation=5, timeout=5, headers={}):
	"""

	从给定的url中下载数据到指定文件中

	:param headers:
	:param url:要下载的资源路径
	:param filename:下载保存的文件位置
	:param self_rotation:自旋报错次数
	:param timeout:超时时间
	:return:
	"""
	socket.setdefaulttimeout(timeout)
	if headers:
		header_list = []
		for key in headers:
			header_list.append((key, headers[key]))
		opener = urllib.request.build_opener()
		opener.addheaders=header_list
		urllib.request.install_opener(opener)
	count = 0
	while count <= self_rotation:
		try:
			request.urlretrieve(url, filename)
			break
		except socket.timeout:
			if count > 5:
				print("from ", url, " download job failed!")
				raise RuntimeError('尝试%d次下载失败,网络异常!' % self_rotation)
			err_info = 'Reloading for %d time' % count if count == 1 else 'Reloading for %d times' % count
			print(err_info)
			count += 1
