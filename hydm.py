# -*- coding: utf-8 -*-
#行业代码处理
import numpy as np
import pandas as pd



filename='D:\\福田决策文件\\企业相关数据\\hydm.csv'
with open(filename, "r", encoding='utf-8',newline='') as file:
	df = pd.read_csv(file, dtype=str)
	df.drop(df.columns[0], axis=1, inplace=True)
	type=df.copy().groupby(['门类']).head(1)
	type.drop(['大类','中类','小类','说    明'], axis=1, inplace=True)
	type.rename(columns={'类 别 名 称': '大类名称'}, inplace=True)
	result=pd.merge(df,type,'left',on='门类')
	df['大类'] = df['大类'].astype(np.str_)
	print(result)
	result.to_csv("D:\\福田决策文件\\企业相关数据\\hydm_处理.csv",
				  index=False,
				  sep=',')