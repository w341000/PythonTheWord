# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from pandas import DataFrame

import spider_util

#获取学校学区信息
xx_url='http://map.28dat.net/s_ft/school.aspx?no=101'
cz_url='http://map.28dat.net/s_ft/school.aspx?no=225'#初中
url_arr=[]
url_arr.append(xx_url)
url_arr.append(cz_url)
schoolarea = []
for url in url_arr:
	html = spider_util.open_url(url, self_rotation=5, timeout=20)  # 20秒超时
	bsObj = BeautifulSoup(html, "html.parser", from_encoding="utf-8")
	a_tags=bsObj.find('span',{'id':'s_school'}).find_all('a')
	for a_tag in a_tags:
			schoolname=a_tag.get_text()
			url='http://map.28dat.net/s_ft/school.aspx'+a_tag.get('href')
			html = spider_util.open_url(url, self_rotation=5, timeout=20)  # 20秒超时
			bsObj = BeautifulSoup(html, "html.parser", from_encoding="utf-8")
			span=bsObj.find('span',{'id':'s_list'})
			area_text=span.get_text()
			area_text_arr=area_text.split('，')
			for text in area_text_arr:
				area = {}
				area['学校名称'] = schoolname
				area['区域范围']=text
				schoolarea.append(area)

DataFrame(schoolarea).to_csv("D:\\011111111111111111111111\\软件\\school_area.csv", index=False, sep=',')




