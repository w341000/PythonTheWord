# -*- coding: utf-8 -*-
# 爬虫工具类
from urllib.request import urlopen
import os

import re


def open_url(url, self_rotation=5, timeout=5):
	"""
	打开url,如果超时则自旋重试,重试次数太多则放弃并抛出异常
	:param url: 要打开的url地址
	:param self_rotation: 自旋次数
	:param timeout: 超时时间
	:return:
	:raise RuntimeError: 失败次数超过允许的自旋重试次数,则抛出此异常
	"""
	i = 0
	while i < self_rotation:
		try:
			html = urlopen(url, timeout=timeout).read()
			return html
		except Exception as e:
			print("从url发生连接错误,尝试重新获取连接:" + repr(e))
			i += 1
			continue
	raise RuntimeError('尝试%d次连接失败,网络异常!' % self_rotation)


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
