# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import datetime


def formatDate(row):
	timestr = row['月份']
	time = datetime.datetime.strptime(timestr, '%Y%m').date()
	tempData = datetime.datetime.strftime(time, "%Y-%m")
	row['月份'] = tempData
	addr = row['现在地址']
	if addr is None or addr is '' or (isinstance(addr, float) and np.isnan(addr)):
		return row
	row['现在地址'] = addr[3:6]
	return row


filename = 'E:\\svnrepo\\python\\03data\\data\\其他来源\\外迁企业相关\\电信数据\\企业迁移情况透视.csv'
with open(filename, "r", encoding='utf-8', newline='') as file:
	dftotal = pd.read_csv(file, dtype=str)
	dftotal.apply(formatDate, axis=1)
	dftotal.to_csv(filename, index=False, sep=',')
