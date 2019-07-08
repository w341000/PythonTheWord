# -*- coding: utf-8 -*-
import pandas as pd
import os
import math
from bs4 import BeautifulSoup
from pandas import DataFrame
import datetime
from util import spider_util


def cleanNumber(df: DataFrame):
	df['格式化电话'] = None
	df['财务固话'].astype('str')
	df['财务固话'].fillna(value='', inplace=True)
	df['号码类型'] = None
	for i in range(len(df)):
		tel = str(df.iloc[i]['财务固话'])
		format_tel = ''
		# print(type(df.iloc[i]['财务固话']))
		# print(df.iloc[i]['财务固话'])
		type = '固话'
		if tel == '':
			format_tel = ''
			type = ''
		elif tel.startswith('1'):  # 1开头为手机号
			format_tel = tel
			type = '手机号'
		elif tel.startswith('0755-'):  # 已经有深圳市区号
			format_tel = '0755-' + tel[5:13]
		elif tel.startswith('0755'):
			format_tel = '0755-' + tel[4:12]
		elif tel.startswith('0'):  # 以0开头，但不是深圳市的区号
			format_tel = tel
			idx = tel.find('-')
			idx2 = tel.find('-', idx + 1)
			if idx2 != -1:
				format_tel = tel[:idx2]
		else:
			format_tel = '0755-' + tel[:8]
		# df.iloc[i]['格式化电话'] = format_tel
		format_tel = format_tel.replace('-', '')
		df.at[i, '格式化电话'] = format_tel
		df.at[i, '号码类型'] = type


def query_location2(df: DataFrame):
	df['号码归属地'] = None
	length = len(df)
	for i in range(length):
		format_tel = df.at[i, '格式化电话']
		if format_tel is None or format_tel == '':
			continue
		url = 'https://www.00cha.com/114.asp?t=' + format_tel
		bsObj = spider_util.open_url_return_bsobj(url, 5, 20,
												  from_encoding='gbk')  # 20秒超时 对于申明编码为gb2312但使用了gbk中的字符时，BeautifulSoup会把编码识别为windows-1252
		tags = bsObj.find_all('font', {'size': 4})
		if tags is None:
			tags = bsObj.find_all('font', {'color': '#008080'})
		text = None
		for tag in tags:
			text = text + ' ' + tag.get_text().strip()
		if format_tel.startswith('0769'):
			text = '广东 东莞'
		df.at[i, '号码归属地'] = text
		spider_util.log_progress(i, length)


def query_location(df: DataFrame):
	df['号码归属地'] = None
	length = len(df)
	for i in range(length):
		format_tel = df.at[i, '格式化电话']
		type = df.at[i, '号码类型']
		if format_tel is None or format_tel == '':
			continue
		if type == '手机号':
			text = query_mobile_phone_location(format_tel)
		else:
			text = query_telphone_location(format_tel)
		df.at[i, '号码归属地'] = text
		spider_util.log_progress(i, length)


def query_telphone_location(tel: str):
	url = 'http://www.zou114.com/tel/' + tel + '.html'
	bsObj = spider_util.open_url_return_bsobj(url, 5, 20,
											  from_encoding='gbk')  # 20秒超时 对于申明编码为gb2312但使用了gbk中的字符时，BeautifulSoup会把编码识别为windows-1252
	tags = bsObj.find_all('font', {'size': 4})
	if tags is None:
		tags = bsObj.find_all('font', {'color': '#008080'})
	text = ''
	for tag in tags:
		text = text + ' ' + tag.get_text().strip()
	return text


def query_telphone_location_114best(tel: str):
	url = 'http://www.114best.com/dh/114.aspx?w=' + tel
	bsObj = spider_util.open_url_return_bsobj(url, 5, 20,
											  from_encoding='gbk')  # 20秒超时 对于申明编码为gb2312但使用了gbk中的字符时，BeautifulSoup会把编码识别为windows-1252
	tags = bsObj.find_all('font', {'size': 4})
	if tags is None:
		tags = bsObj.find_all('font', {'color': '#008080'})
	text = ''
	for tag in tags:
		text = text + ' ' + tag.get_text().strip()
	return text


def query_mobile_phone_location(tel: str):
	url = 'http://www.zou114.com/shouji/?mobile='+ tel
	bsObj = spider_util.open_url_return_bsobj(url, 5, 20,
											  from_encoding='gbk')  # 20秒超时 对于申明编码为gb2312但使用了gbk中的字符时，BeautifulSoup会把编码识别为windows-1252
	div=bsObj.select_one('.nrbnr')
	tags = div.find_all('font', {'color': 'red'})
	text=''
	if tags is not None :
		text=tags[0].get_text()+' ;卡类型：'+tags[1].get_text()
	return text


def main():
	df = pd.read_excel('D:\\tmp\\企业服务中心企业电话号码.xlsx')
	cleanNumber(df)
	query_location(df)
	df.to_excel('D:\\tmp\\企业服务中心企业电话号码.xlsx', index=False)


if __name__ == '__main__':
	main()
# tel = '00751112'
# print(tel.startswith('0075'))
