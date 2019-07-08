# -*- coding: utf-8 -*-
import pandas as pd
from bs4 import BeautifulSoup
from util import spider_util, coordinate_util
import math
import time
# 修改坐标
def change_zb(filename):
	with open(filename, "r", encoding='utf-8', newline='') as file:
		header={'Cookie':'BCE54B84-5407-41FD-9D16-C8A09E5DA2A0=YWRtaW4%3D; YWRtaW4==a2RpZiNzaWM4RGpbY216; JSESSIONID=1BA5932F6535DFDEAA2E63C9AAD3040C'}
		url='http://10.169.11.195:7020/tjfxpt/gis/local2wgs.xhtml'
		df = pd.read_csv(file, dtype=str)
		length=len(df.index)
		df['bd_x'] = None
		df['bd_y'] = None
		df['gd_x'] = None
		df['gd_y'] = None
		for x in range(len(df.index)):
			try:
				ABSX=df['LOG'].iloc[x]
				ABSY=df['LAT'].iloc[x]
				if ABSY is None or ABSY is None:
					continue
				ABSX = float(ABSX)
				ABSY = float(ABSY)
				if math.isnan(ABSX) or math.isnan(ABSY):#非数字跳过
					continue
				html = spider_util.open_url(url, data={'lng': ABSX, 'lat': ABSY},header=header)
				bsObj = BeautifulSoup(html, "html.parser", from_encoding="utf-8")
				zb = bsObj.get_text().strip()
				zb_arr = zb.split(',')
				lon = float(zb_arr[0])  # 百度经度坐标
				lat = float(zb_arr[1])
				df.set_value(x, 'bd_x', lon)
				df.set_value(x, 'bd_y', lat)
				gcj02=coordinate_util.bd09togcj02(lon,lat)#百度坐标转火星坐标
				df.set_value(x, 'gd_x', gcj02[0])
				df.set_value(x, 'gd_y', gcj02[1])
				spider_util.log_progress(x,length,start_from_zero=True,detailedLog=True)
				# print(jd84+'-----'+wd84
				# time.sleep(0.04)
			except Exception as e:
					print('跳过该条数据')
		df.to_csv(filename, index=False, sep=',')
		print(df)

if __name__ == '__main__':
	filename='C:\\Users\\admin\\Desktop\\DWR_MDM_BUILD_INFO_DIM.csv'
	change_zb(filename)