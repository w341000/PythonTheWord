# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from pandas import DataFrame
import zb_zhuanhuan
import spider_util
import math
import time

# 修改坐标
def change_zb(filename):
	url='http://192.168.37.134:8080/ConvertCoord/servlet/local2wgs'
	with open(filename, "r", encoding='utf-8',newline='') as file:
		df = pd.read_csv(file, dtype=str)
		df['84_x']=None
		df['84_y'] = None
		df['bd_x'] = None
		df['bd_y'] = None
		df['gd_x'] = None
		df['gd_y'] = None
		for x in range(len(df.index)):
			try:
				ABSX=df['LON'].iloc[x]
				ABSY=df['LAT'].iloc[x]
				if ABSY is None or ABSY is None:
					continue
				ABSX = float(ABSX)
				ABSY = float(ABSY)
				if math.isnan(ABSX) or math.isnan(ABSY):#非数字跳过
					continue
				html = spider_util.open_url(url, data={'lat': ABSX, 'lon': ABSY})
				bsObj = BeautifulSoup(html, "html.parser", from_encoding="utf-8")
				zb = bsObj.get_text().strip()
				zb_arr = zb.split(',')
				lon = float(zb_arr[0])  # 84经度坐标
				lat = float(zb_arr[1])
				df.set_value(x, '84_x', lon)
				df.set_value(x, '84_y', lat)
				gcj02=zb_zhuanhuan.wgs84togcj02(lon,lat)#84坐标转火星坐标
				df.set_value(x, 'gd_x', gcj02[0])
				df.set_value(x, 'gd_y', gcj02[1])
				bd09=zb_zhuanhuan.gcj02tobd09(gcj02[0],gcj02[1])#火星坐标转百度坐标
				df.set_value(x, 'bd_x', bd09[0])
				df.set_value(x, 'bd_y', bd09[1])
				# print(jd84+'-----'+wd84)


				time.sleep(0.04)
			except Exception as e:
					print('跳过该条数据')


		df.to_csv(filename, index=False, sep=',')

if __name__ == '__main__':
	filename='C:\\Users\\admin\\Desktop\\快数据-楼栋信息.csv'
	change_zb(filename)