# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from pandas import DataFrame

import spider_util

url='http://10.190.62.57/geostar/440304_schooldistrict/wfs?VERSION=1.0.0&SERVICE=WFS&REQUEST=GetFeature&RESULTTYPE=result&OUTPUTFORMAT=XML'
html = spider_util.open_url(url, self_rotation=5, timeout=20)  # 20秒超时
bsObj = BeautifulSoup(html,  "lxml-xml", from_encoding="utf-8")
features=bsObj.find_all('gml:featureMember')
schoolarea=[]
for feature in features:
	school=None;
	schoolType=2;
	school=feature.find('MIDDLESCHOOL')
	if school is None:
		school = feature.find('PRIMARYSCHOOL')
		schoolType=1
	schoolObj={}
	position=school.find('gml:coordinates').get_text()
	schoolname=school.find('NAME').get_text()
	schoolObj['schoolType']=schoolType
	schoolObj['schoolName']=schoolname
	schoolObj['position']=position
	schoolarea.append(schoolObj)
DataFrame(schoolarea).to_csv("D:\\011111111111111111111111\\软件\\school_area_data.csv", index=False, sep=',')