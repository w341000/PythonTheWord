# -*- coding: utf-8 -*-
from util import spider_util
from bs4 import BeautifulSoup
import json
import demjson
import pandas as pd
from pandas import DataFrame
import urllib
from util import coordinate_util
from urllib.request import urlopen
from urllib import error
import json
import numpy as np
from util import db_util
import os


def request_area_building():
	"""
	获取学区图中每个学区的0-18岁人口信息
	:return: DataFrame
	"""
	file = 'D:\\pypy\\pythonresult\\教育学位\\学校人口信息.xls'
	if os.path.isfile(file):
		area_data = DataFrame(pd.read_excel(file))
		if area_data is not None or not area_data.empty:
			return area_data
	areas = DataFrame(pd.read_excel('D:\\pypy\\pythonresult\\教育学位\\学区信息.xls'))
	data = {'f': 'json', 'returnGeometry': 'false', 'spatialRel': 'esriSpatialRelIntersects',
			'geometryType': 'esriGeometryPolygon', 'inSR': 4490, 'outFields': 'BLDG_NO,NOWNAME', 'outSR': 4490}
	url_prefox = 'http://10.190.55.55:8080/arcgis/rest/services/FTKSJ/JZWDLM_CGCS2000/MapServer/1/query'
	person_data = DataFrame()
	for index, row in areas.iterrows():
		polygon_84 = row['polygon_84']
		schoolname = row['name']
		if polygon_84 is not None and polygon_84 is not '' and polygon_84 is not np.nan:
			geometry = split_point_to_geometry(polygon_84)
			data['geometry'] = geometry
			result = spider_util.open_url(url_prefox, 5, 20, data=data)  # 20秒超时
			jsondata = demjson.decode(result)
			buildings = get_building(jsondata)
			if buildings is None or len(buildings) == 0:
				print('该学校：' + schoolname + '楼栋id为空')
				continue
			childinfo = request_area_personcont(schoolname, buildings)
			person_data = person_data.append(childinfo)
	df = DataFrame(person_data)
	df.to_excel(file, index=False)
	return df


def get_building(jsondata):
	features = jsondata['features']
	buildings = []
	for feature in features:
		building_no = feature['attributes']['BLDG_NO']
		buildings.append(building_no)
	return buildings


def request_area_personcont(school: str, buildings: []):
	result = None
	num = int(len(buildings) / 999) + 1
	split_buildings = np.array_split(buildings, num)
	for split_building in split_buildings:
		try:
			hjrk_sql = "SELECT age,sum(num) NUM,RKXZ FROM FT_RKJZT WHERE lddm IN(%s) AND age <18 AND AGE >=0 and rkxz='深圳户籍人口'  GROUP BY AGE,RKXZ"
			ldrk_sql = "SELECT age,sum(num) NUM,RKXZ FROM FT_RKJZT WHERE lddm IN(%s) AND age <18 AND AGE >=0 and rkxz='流动人口'  GROUP BY AGE,RKXZ"
			# url='http://localhost:8080/ftidss/edu/getAgeJZTbyByildings.do'
			# header={'Cookie': 'shiro.session.id=8d73795b-2ce6-495b-ae2e-1ef6cd9c39df','Content-Type':'application/json;charset=UTF-8'}
			# data={'buildingIds':buildings}
			# request = urllib.request.Request(url, json.dumps(data).encode('utf-8'), header)
			# jsondata = demjson.decode(urlopen(request, timeout=10).read())
			# result=jsondata['result']
			# for item in result:
			# 	item['school']=school
			in_p = ', '.join(list(map(lambda x: "'%s'" % x, split_building)))
			hjrk_sql = hjrk_sql % in_p
			ldrk_sql = ldrk_sql % in_p
			hrjk_df = db_util.execute2Dataframe(hjrk_sql)
			ldrk_df = db_util.execute2Dataframe(ldrk_sql)
			if result is not None:
				result = hrjk_df.add(result, fill_value=0)
			else:
				result = hrjk_df
			if result is not None:
				result = ldrk_df.add(result, fill_value=0)
			else:
				result = ldrk_df
		except Exception as e:
			print(e)
	result['SCHOOLNAME'] = school
	return result


def split_point_to_geometry(polygon_84: str):
	points = polygon_84.split(';')
	area = []
	geometry = {'rings': [area]}
	for point in points:
		zbarr = point.split(',')
		area.append(zbarr)
	return geometry


if __name__ == '__main__':
	df = request_area_building()
	print(df)
