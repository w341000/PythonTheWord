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
import sqlalchemy

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
	areas = db_util.execute2Dataframe('SELECT\
				WWYJFX.T_JY_SCHOOLAREA.SCHOOLNAME,\
				WWYJFX.T_JY_SCHOOLAREA.SCHOOL_FULLNAME,\
				WWYJFX.T_JY_SCHOOLAREA.SCHOOLTYPE,\
				WWYJFX.T_JY_SCHOOLAREA.POLYGON_84\
				FROM\
				WWYJFX.T_JY_SCHOOLAREA\
			')
	# areas = DataFrame(pd.read_excel('D:\\pypy\\pythonresult\\教育学位\\学区信息.xls'))
	data = {'f': 'json', 'returnGeometry': 'false', 'spatialRel': 'esriSpatialRelIntersects',
			'geometryType': 'esriGeometryPolygon', 'inSR': 4490, 'outFields': 'BLDG_NO,NOWNAME', 'outSR': 4490}
	url_prefox = 'http://10.190.55.55:8080/arcgis/rest/services/FTKSJ/JZWDLM_CGCS2000/MapServer/1/query'
	person_data = DataFrame()
	for index, row in areas.iterrows():
		polygon_84 = row['POLYGON_84']
		schoolname = row['SCHOOLNAME']
		schooltype = row['SCHOOLTYPE']
		if polygon_84 is not None and polygon_84 is not '' and polygon_84 is not np.nan:
			geometry = split_point_to_geometry(polygon_84)
			data['geometry'] = geometry
			result = spider_util.open_url(url_prefox, 5, 20, data=data)  # 20秒超时
			jsondata = demjson.decode(result)
			buildings = get_building(jsondata)
			if buildings is None or len(buildings) == 0:
				print('该学校：' + schoolname + '楼栋id为空')
				continue
			childinfo = request_area_personcont(schoolname, schooltype, buildings)
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


def request_area_personcont(school: str, schooltype: str, buildings: []):
	num = int(len(buildings) / 999) + 1
	split_buildings = np.array_split(buildings, num)
	hrjk_dict = {}
	ldrk_dict = {}
	hrjk_list=[]
	ldrk_list = []
	for split_building in split_buildings:
		try:
			hjrk_sql = "SELECT age,sum(num) NUM,RKXZ FROM FT_RKJZT WHERE lddm IN(%s) AND age <18 AND AGE >=0 AND rkxz='深圳户籍人口'  GROUP BY AGE,RKXZ"
			ldrk_sql = "SELECT age,sum(num) NUM,RKXZ FROM FT_RKJZT WHERE lddm IN(%s) AND age <18 AND AGE >=0 AND rkxz='流动人口'  GROUP BY AGE,RKXZ"
			in_p = ', '.join(list(map(lambda x: "'%s'" % x, split_building)))
			hjrk_sql = hjrk_sql % in_p
			ldrk_sql = ldrk_sql % in_p
			hrjk_df = db_util.execute2Dataframe(hjrk_sql)
			ldrk_df = db_util.execute2Dataframe(ldrk_sql)
			for index,row in hrjk_df.iterrows():
				age=row['AGE']
				num=row['NUM']
				if not hrjk_dict.get(age):
					hrjk_dict[age]=0
				hrjk_dict[age]=hrjk_dict[age]+num
			for index,row in ldrk_df.iterrows():
				age=row['AGE']
				num=row['NUM']
				if not ldrk_dict.get(age):
					ldrk_dict[age]=0
				ldrk_dict[age] = ldrk_dict[age] + num
		except Exception as e:
			print(e)
	for age in hrjk_dict:
		hrjk_list.append({'AGE':age,'NUM':hrjk_dict[age],'RKXZ':'深圳户籍人口','SCHOOLNAME':school,'SCHOOLTYPE':schooltype})
	for age in ldrk_dict:
		ldrk_list.append({'AGE':age,'NUM':ldrk_dict[age],'RKXZ':'流动人口','SCHOOLNAME':school,'SCHOOLTYPE':schooltype})
	hrjk_list.extend(ldrk_list)
	return DataFrame(hrjk_list)


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
