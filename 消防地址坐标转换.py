# -*- coding: utf-8 -*-
import spider_util
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
from pandas import DataFrame, Series
import math
import json
import  urllib
import numpy as np
filename = 'E:\\svnrepo\\python\\03data\\data\\各委办局直接过来的数据\\消防数据\\0808福田消防数据\\福田建筑.csv'
with open(filename, "r", encoding='utf-8',newline='') as file:
	df = pd.read_csv(file, dtype=str)
	df['STREET'] = None
	df['COMMUNITY'] = None
	df['FWDM'] = None
	df['FWDM'] = None
	for x in range(len(df.index)):
		addr = df['BUILD_ADDR'].iloc[x]
		if addr is None or addr=='' or (isinstance(addr,float) and np.isnan(addr)):
			continue
		try:
			url = 'http://10.190.62.81/EarthService/services/address/matchAddress?address='+urllib.parse.quote(addr)+'&max=1&_type=json&user=yongtai&token=yongtai_address'
			html = spider_util.open_url(url,data=None)
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
	df.to_csv('E:\\svnrepo\\python\\03data\\data\\各委办局直接过来的数据\\消防数据\\0808福田消防数据\\福田建筑(增加地址信息及房屋编码).csv',index=False, sep=',')

