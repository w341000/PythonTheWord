# -*- coding: utf-8 -*-
from pandas import DataFrame, Series
import pandas as pd
import collections
from util import address_standardization,coordinate_util
filename = 'C:\\Users\\admin\\Desktop\\开放平台住建局相关\\2018年人才住房和保障性住房项目信息.csv'
# filename='d:\\progressIndex.csv'
with open(filename, "r", encoding='utf-8',newline='') as file:
	df = pd.read_csv(file, dtype=str)
	for x in range(len(df.index)):
		addr = df['XMJTWZ'].iloc[x]
		try:
			addressComponent=comment=address_standardization.formatAddress(addr)
		except Exception as e:
			addressComponent=collections.defaultdict(str)
		df.set_value(x, 'QU', addressComponent['district'])
		df.set_value(x, 'STREET', addressComponent['town'])
		df.set_value(x, 'DL', addressComponent['street'])
		df.set_value(x, 'BD_X', addressComponent['bd_x'])
		df.set_value(x, 'BD_Y', addressComponent['bd_y'])
		df.set_value(x, 'LON84', addressComponent['lon84'])
		df.set_value(x, 'LAT84', addressComponent['lat84'])
	print(df)
	df.to_csv(filename, index=False,sep=',')