# -*- coding: utf-8 -*-
from util import spider_util
import pandas as pd
import json
import  urllib
import numpy as np
filename = 'E:\\svn仓库\\svnrepo\\python\\02clean&model\\data\\消防相关\\18年8月-11月火灾数据.csv'
with open(filename, "r", encoding='utf-8',newline='') as file:
	df = pd.read_csv(file, dtype=str)
	df['STREET'] = None
	df['COMMUNITY'] = None
	df['FWDM'] = None
	for x in range(len(df.index)):
		addr = df['起火地点'].iloc[x]
		if addr is None or addr=='' or (isinstance(addr,float) and np.isnan(addr)):
			continue
		try:
			url = 'http://10.190.62.81/EarthService/services/address/matchAddress?address='+urllib.parse.quote(addr)+'&max=1&_type=json&user=yongtai&token=yongtai_address'
			html = spider_util.open_url(url, data=None)
			addrObj = json.loads(html)['address'][0]
			STREET=addrObj['street'];
			COMMUNITY = addrObj['community'];
			FWDM = addrObj['houseCode'];
			df.set_value(x, 'STREET', STREET)
			df.set_value(x, 'COMMUNITY', COMMUNITY)
			df.set_value(x, 'FWDM', FWDM)
		except Exception as e:
			print('发生错误，跳过该条记录' + str(e))
	print(df)
	df.to_csv(filename,index=False, sep=',')

