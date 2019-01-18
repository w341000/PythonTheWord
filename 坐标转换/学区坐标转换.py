# -*- coding: utf-8 -*-
import pandas as pd
import math
from util import coordinate_util

filename = 'D:\\bsarea.csv'
with open(filename, "r", encoding='utf-8',newline='') as file:
	df = pd.read_csv(file, dtype=str)
	df['POSITION_84'] = None
	for x in range(len(df.index)):
		try:
			POSITION=df['POSITION'].iloc[x]
			if POSITION is None :
				continue
			pos_arr=POSITION.split(';')
			POSITION_84=''
			for pos in pos_arr:
				BD_ARR=pos.split(',')
				BD_X=float(BD_ARR[0])
				BD_Y=float(BD_ARR[1])
				if math.isnan(BD_X) or math.isnan(BD_Y):  # 非数字跳过
					continue
				zb_arr= coordinate_util.bd09towgs84(BD_X, BD_Y)
				lon_84=zb_arr[0]
				LAT_84=zb_arr[1]
				POSITION_84=POSITION_84+' '+str(lon_84)+','+str(LAT_84)
			POSITION_84=POSITION_84[1:]
			df.set_value(x, 'POSITION_84', POSITION_84)
		except Exception as e:
			print('发生错误，跳过该条记录' + str(e))
	print(df)
	df.to_csv(filename,index=False, sep=',')

