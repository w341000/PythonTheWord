# -*- coding: utf-8 -*-
from util import address_standardization
import pandas as pd

filename = 'E:\\svn仓库\\svnrepo\\python\\03data\\data\\爬取数据\\环境相关\\T_HB_NOISELOC.csv'
with open(filename, "r", encoding='utf-8', newline='') as file:
	df = pd.read_csv(file, dtype=str)
	for x in range(len(df.index)):
		lon = df['JD84'].iloc[x]  # 坐标经度
		lat = df['WD84'].iloc[x]  # 坐标纬度
		if lon is None or lon is '':
			continue
		addressComponent = address_standardization.location2normaladdress(lon, lat, coordtype='wgs84ll')
		for key in addressComponent:
			df.set_value(x, key, addressComponent[key])
	print(df)
	df.to_csv(filename, index=False, sep=',')
