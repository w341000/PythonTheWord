# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd


#外迁分数
def wq_score(x):
	if np.isnan(x['外迁概率']) :
		result = float(x['电信分数']) * 0.5
	else:
		result = float(x['电信分数']) * 0.8 + float(x['外迁概率'] * 0.2)
	result=round(result,2)
	return result
#判断风险等级
def level(x):
	if x['外迁分数']<0.4:
		result='低'
	elif x['外迁分数']<0.55:
		result='中'
	else:
		result='高'
	return result

#处理外迁企业
filename='D:\\福田决策文件\\企业相关数据\\外迁0620\\企业外迁预警模型--基于电信数据.csv'
with open(filename, "r", encoding='utf-8',newline='') as file:
	waiqianfile = 'D:\\福田决策文件\\企业相关数据\\外迁0620\\外迁模型01.csv'
	with open(waiqianfile, "r", encoding='utf-8', newline='') as waiqianfile:
		df=pd.read_csv(file)
		df.drop(df.columns[3:], axis=1, inplace=True)
		df.drop(df.columns[0], axis=1, inplace=True)
		df['外迁分数']=None
		df.loc[df['识别原因'] == '近期大量装移拆', '电信分数'] = '0.8'
		df.loc[df['识别原因'] == '近期高比例固网移机', '电信分数'] = '0.7'
		df.loc[df['识别原因'] == '近期高比例固网拆除', '电信分数'] = '0.6'

		df2 = pd.read_csv(waiqianfile)
		df2.drop(df2.columns[0], axis=1, inplace=True)
		result=pd.merge(df,df2,'left',left_on='公司名称',right_on='企业名称')
		result['外迁分数'] = result.apply(wq_score, axis=1)
		result['风险等级'] = result.apply(level, axis=1)
		result.drop(['企业名称'],axis=1, inplace=True)
		result.rename(columns={'外迁概率': '外迁模型分数'}, inplace=True)
		result.to_csv("D:\\福田决策文件\\企业相关数据\\外迁0620\\外迁企业数据.csv",
								index=False,
								sep=',')
