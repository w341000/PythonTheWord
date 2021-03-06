# -*- coding: utf-8 -*-
import pandas as pd
from bs4 import BeautifulSoup
from util import spider_util, coordinate_util
import math
import time

# 修改坐标
def change_zb(filename):
	url='http://192.168.37.134:8080/ConvertCoord/servlet/wgs2local'
	with open(filename, "r", encoding='utf-8',newline='') as file:
		df = pd.read_csv(file, dtype=str)
		df['pointx']=None
		df['pointy'] = None
		for x in range(len(df.index)):
			try:
				ABSX=df['ABSX'].iloc[x]
				ABSY=df['ABSY'].iloc[x]
				if ABSY is None or ABSY is None:
					continue
				ABSX = float(ABSX)
				ABSY = float(ABSY)
				if math.isnan(ABSX) or math.isnan(ABSY):#非数字跳过
					continue
				wgs84= coordinate_util.gcj02towgs84(ABSX, ABSY)
				jd84=wgs84[0]
				wd84=wgs84[1]
				# print(jd84+'-----'+wd84)
				html = spider_util.open_url(url, data={'lat': jd84, 'lon': wd84})
				bsObj = BeautifulSoup(html, "html.parser", from_encoding="utf-8")
				zb = bsObj.get_text().strip()
				zb_arr = zb.split(',')
				lon = zb_arr[0]  # 经度坐标
				lat = zb_arr[1]
				df.set_value(x,'pointx',lon)
				df.set_value(x,'pointy',lat)
				time.sleep(0.04)
			except Exception as e:
					print('跳过该条数据')


		df.to_csv(filename, index=False, sep=',')

if __name__ == '__main__':
	filename='D:\\福田决策文件\\临时\\T_YW_ZZ_SJ.csv'
	change_zb(filename)