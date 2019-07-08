# -*- coding: utf-8 -*-
import pandas as pd
import os
import math
from urllib import request
import xlsxwriter
from bs4 import BeautifulSoup
from pandas import DataFrame
import datetime
from util import spider_util
from urllib.parse import urljoin
from PIL import Image
import random
import time
import uuid
filename = 'D:\\tmp\\企业服务中心企业电话号码-图片版本.xlsx'
test_book = xlsxwriter.Workbook(filename)
worksheet = test_book.add_worksheet('what')
bold = test_book.add_format({'bold': True})


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


def query_location(df: DataFrame):
	df['号码归属地'] = None
	length = len(df)
	# for i in range(length):
	# 	format_tel = df.at[i, '格式化电话']
	# 	type = df.at[i, '号码类型']
	# 	if format_tel is None or format_tel == '':
	# 		continue
	# 	if type == '手机号':
	# 		text = query_mobile_phone_location(format_tel)
	# 	else:
	# 		text = query_telphone_location(format_tel)
	# 	df.at[i, '号码归属地'] = text
	# 	spider_util.log_progress(i, length)
	worksheet.write_row(0, 0, ['企业名称', '企业电话', '电话归属地', '格式化后的电话'])
	for i, row in df.iterrows():
		try:
			index = i + 1
			company = row['纳税人名称']
			tel = row['财务固话']
			format_tel = row['格式化电话']
			worksheet.write(index, 0, company)
			worksheet.write(index, 1, tel)
			if format_tel is None or format_tel == '':
				continue
			while True:
				try:
					pic_path = download_pic(format_tel)
					break
				except Exception as e:
					print('发生连接错误，睡眠一段时间后后尝试重新连接')
					print(repr(e))
					time.sleep(120)
					continue
			if pic_path is not None and not pic_path == '':
				worksheet.insert_image(index, 2, pic_path)
			worksheet.write(index, 3, format_tel)
			spider_util.log_progress(i, length)
			sellp_time = random.randint(2, 4)
			time.sleep(sellp_time)
			if i >= 2000:
				break
		except Exception as e:
			print('发生异常信息，跳过该号码', repr(e))
			continue

	test_book.close()


# 下载图片
def download_pic(tel: str):
	url = 'http://www.114best.com/dh/114.aspx?w=' + tel
	bsObj = spider_util.open_url_return_bsobj(url, 5, 20,
											  from_encoding='gbk')
	try:
		img_tag = bsObj.select_one('#span_gsd img')
		if img_tag is None:
			return None
		src = img_tag.get('src')
		gif_link = urljoin(url, src)
		local_filename = 'D:\\tmp\\wj\\temp.gif'
		spider_util.download(gif_link,local_filename,3,10)
		# request.urlretrieve(gif_link, local_filename)
		fp = open(local_filename, 'rb')
		img = Image.open(fp)
		Img = img.convert('L')
		threshold = 200
		table = []
		for i in range(256):
			if i < threshold:
				table.append(0)
			else:
				table.append(1)

		# 图片二值化
		photo = Img.point(table, '1')
		uuid_str = str(uuid.uuid1())
		black_pic = 'D:\\tmp\\wj\\temppng\\'+uuid_str+'.png'
		photo.save(black_pic)
		fp.close()
		os.remove(local_filename)  # 删除gif文件
		return black_pic
	except Exception as e:
		print('发生异常行为',repr(e))
		return None


def main():
	df = pd.read_excel('D:\\tmp\\企业服务中心企业电话号码.xlsx')
	cleanNumber(df)
	query_location(df)


# df.to_excel('D:\\tmp\\企业服务中心企业电话号码-图片版本.xlsx', index=False)


if __name__ == '__main__':
	main()
# tel = '00751112'
# print(tel.startswith('0075'))
