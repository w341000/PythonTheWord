# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from pandas import  DataFrame

#对户籍地址进行过滤添加户籍省


def hj(x):
	zzq=['内蒙古自治区','新疆维吾尔自治区','广西壮族自治区','宁夏回族自治区','西藏自治区']
	zxs=['北京市','上海市','天津市','重庆市']
	hjs=x['HJS']
	if np.isnan(hjs):
		pass
	for i in range(len(zzq)):#自治区判断
		wz=zzq[i]
		if wz in hjs:
			if i ==0:
				return wz[:3]
			else:
				return wz[:2]
	for wz in zxs:#直辖市判断
		if wz in hjs:
			return wz[:2]

	idx=hjs.find('省')
	if idx!=-1:
		return hjs[:idx]

	return hjs




def main():
	filename='D:\\福田决策文件\\人口相关数据\\T_YW_ZZ_PERSON_BASE.csv'
	with open(filename, "r", encoding='utf-8',newline='') as file:
		df = pd.read_csv(file, dtype=str)
		df['hj'] = df.apply(hj, axis=1)
		df.to_csv("D:\\福田决策文件\\人口相关数据\\T_YW_ZZ_PERSON_BASE_clean.csv",
				  index=False,
				  sep=',')

DataFrame()
