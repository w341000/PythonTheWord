# -*- coding: utf-8 -*-
from util import coordinate_util
import pandas as pd
import math

filename = 'E:\\svn仓库\\svnrepo\\python\\02clean&model\\data\\1009坐标转换涉及数据\\T_O_SCHOOLINFO_BASE.csv'
with open(filename, "r", encoding='utf-8',newline='') as file:
	df = pd.read_csv(file, dtype=str)
	df['LON_84'] = None
	df['LAT_84'] = None
	for x in range(len(df.index)):
		try:
			SZ_X=df['POINTX'].iloc[x]
			SZ_Y=df['POINTY'].iloc[x]
			if SZ_X is None or SZ_X is None:
				continue
			SZ_X = float(SZ_X)
			SZ_Y = float(SZ_Y)
			if math.isnan(SZ_X) or math.isnan(SZ_X):  # 非数字跳过
				continue
			zb_arr= coordinate_util.sz2wgs84(SZ_X, SZ_Y)
			lon_84=zb_arr[0]
			LAT_84=zb_arr[1]
			df.set_value(x, 'LON_84', lon_84)
			df.set_value(x, 'LAT_84', LAT_84)
		except Exception as e:
			print('发生错误，跳过该条记录' + str(e))
	print(df)
	df.to_csv(filename,index=False, sep=',')

