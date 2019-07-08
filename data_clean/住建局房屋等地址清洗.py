# -*- coding: utf-8 -*-
from pandas import DataFrame, Series
import pandas as pd
import collections
from util import spider_util
from util import address_standardization,coordinate_util
from util import db_util


def format():
	df =db_util.execute2Dataframe('select * from T_OPEN_SGXKZXX ')
	dflen=len(df.index)#总行数
	for x in range(dflen):
		addr = df['CONST_LOCATION'].iloc[x]
		try:
			addressComponent=address_standardization.formatAddress(addr)

			df.set_value(x, 'QU', addressComponent['district'])
			df.set_value(x, 'STREET', addressComponent['town'])
			df.set_value(x, 'DL', addressComponent['street'])
			df.set_value(x, 'BD_X', addressComponent['bd_x'])
			df.set_value(x, 'BD_Y', addressComponent['bd_y'])
			df.set_value(x, 'LON84', addressComponent['lon84'])
			df.set_value(x, 'LAT84', addressComponent['lat84'])
		except Exception as e:
			print('地址转换错误：',addr,e)
		spider_util.log_progress(x,dflen)
	print(df)
	df.to_excel('D:\\011111111111111111111111\\00临时文件\\T_OPEN_SGXKZXX.xlsx', index=False)


if __name__=='__main__':
	format()