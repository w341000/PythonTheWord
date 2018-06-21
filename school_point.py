# -*- coding: utf-8 -*-
import csv
import json
import urllib
from urllib import parse

from pandas import DataFrame

import spider_util


def readCSV2List(filePath):
	with open(filePath, newline='',
			  encoding='utf-8') as csvfile:  # 此方法:当文件不用时会自动关闭文件
		csvReader = csv.DictReader(csvfile)
		reader = csv.reader(csvfile)
		csvHead = csvReader.fieldnames
		print(csvHead)
		table_list = []
		for content in csvReader:
			data={}
			for head in csvHead:
				data[head]=content[head]
			table_list.append(data)
		return table_list
headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)', 'Host': '10.190.65.123:6080',
			   'Pragma': 'no-cache'
		, 'Upgrade-Insecure-Requests': '1'
		, 'Accept': '*/*'
		, 'Accept-Language': 'zh-CN,zh;q=0.9'}
datas=readCSV2List('D:\\项目temp\\school_new.csv')
for school in datas:
	data={'geometryType': 'esriGeometryEnvelope',
'spatialRel': 'esriSpatialRelIntersects',
'returnGeometry': 'true',
'returnTrueCurves': 'false',
'returnIdsOnly': 'false',
'returnCountOnly': 'false',
'returnZ': 'false',
'returnM': 'false',
'returnDistinctValues': 'false',
'f': 'pjson'}
	data['where']="标准名 like '%"+school['学校名称']+"%'"
	type=school['学校类型']
	if type ==1 or type=='1':
		url='http://10.190.65.123:6080/arcgis/rest/services/FTKSJ/ggss_futian_201803_01/MapServer/102/query'
	elif type== 2 or type =='2':
		url='http://10.190.65.123:6080/arcgis/rest/services/FTKSJ/ggss_futian_201803_01/MapServer/101/query'
	elif type ==0 or type =='0':
		url='http://10.190.65.123:6080/arcgis/rest/services/FTKSJ/ggss_futian_201803_01/MapServer/103/query'
	#req = request.Request(url=url,data=data)
	data = urllib.parse.urlencode(data).encode('utf-8')
	html=spider_util.open_url(url,data=data)
	result = json.loads(html)
	features=result['features']
	if features is not None and len(features)>0:
		schoolpt=features[0]
		x=schoolpt.get('geometry').get('x')
		y = schoolpt.get('geometry').get('y')
		school['pointX'] = x
		school['pointY'] = y

DataFrame(datas).to_csv("D:\\项目temp\\school_new_1.csv", index=False, sep=',')