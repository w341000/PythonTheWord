# -*- coding: utf-8 -*-
from util import coordinate_util
import pandas as pd
import math
from util import  address_standardization
filename = 'd:\\test.xlsx'
# with open(filename, "r") as file:
df = pd.read_excel(filename, dtype=str)
df['标准地址']=None
for x in range(len(df.index)):
	try:
		lon=df['经度'].iloc[x]
		lat=df['纬度'].iloc[x]
		if lon is None or lat is None:
			continue
		# SZ_X = float(SZ_X)
		# SZ_Y = float(SZ_Y)
		address=address_standardization.location2normaladdress(lon,lat,'wgs84ll')
		formatted_address=address['formatted_address']
		df.set_value(x, '标准地址', formatted_address)
		# df.set_value(x, 'LAT_84', LAT_84)
		print(formatted_address)
	except Exception as e:
		print('发生错误，跳过该条记录' + str(e))

print(df)

df.to_excel(filename,index=False)
