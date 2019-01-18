# -*- coding: utf-8 -*-
import pandas as pd
import math
from util import coordinate_util

filename = 'E:\\svn仓库\\svnrepo\\python\\02clean&model\\data\\1009坐标转换涉及数据\\T_YW_ZZ_SJ.csv'
with open(filename, "r", encoding='utf-8',newline='') as file:
	df = pd.read_csv(file, dtype=str)
	df['LON_84'] = None
	df['LAT_84'] = None
	for x in range(len(df.index)):
		try:
			BD_X=df['ABSX'].iloc[x]
			BD_Y=df['ABSY'].iloc[x]
			if BD_X is None or BD_Y is None:
				continue
			BD_X = float(BD_X)
			BD_Y = float(BD_Y)
			if math.isnan(BD_X) or math.isnan(BD_Y):  # 非数字跳过
				continue
			zb_arr= coordinate_util.bd09togcj02(BD_X, BD_Y)
			zb_84_arr= coordinate_util.gcj02towgs84(zb_arr[0], zb_arr[1])
			lon_84=zb_84_arr[0]
			LAT_84=zb_84_arr[1]
			df.set_value(x, 'LON_84', lon_84)
			df.set_value(x, 'LAT_84', LAT_84)
		except Exception as e:
			print('发生错误，跳过该条记录' + str(e))
	print(df)
	df.to_csv(filename,index=False, sep=',')

