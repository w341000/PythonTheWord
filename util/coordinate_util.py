# -*- coding: utf-8 -*-
import math
from bs4 import BeautifulSoup
from util import spider_util
import time

key = 'your key here'  # 这里填写你的百度开放平台的key
x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 扁率


def gcj02tobd09(lng, lat):
	"""
	火星坐标系(GCJ-02)转百度坐标系(BD-09)
	谷歌、高德——>百度
	:param lng:火星坐标经度
	:param lat:火星坐标纬度
	:return:
	"""
	z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
	theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
	bd_lng = z * math.cos(theta) + 0.0065
	bd_lat = z * math.sin(theta) + 0.006
	return [bd_lng, bd_lat]


def bd09togcj02(bd_lon, bd_lat):
	"""
	百度坐标系(BD-09)转火星坐标系(GCJ-02)
	百度——>谷歌、高德
	:param bd_lat:百度坐标纬度
	:param bd_lon:百度坐标经度
	:return:转换后的坐标列表形式
	"""
	x = bd_lon - 0.0065
	y = bd_lat - 0.006
	z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
	theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
	gg_lng = z * math.cos(theta)
	gg_lat = z * math.sin(theta)
	return [gg_lng, gg_lat]


def wgs84togcj02(lng, lat):
	"""
	WGS84转GCJ02(火星坐标系)
	:param lng:WGS84坐标系的经度
	:param lat:WGS84坐标系的纬度
	:return:
	"""
	if out_of_china(lng, lat):  # 判断是否在国内
		return lng, lat
	dlat = transformlat(lng - 105.0, lat - 35.0)
	dlng = transformlng(lng - 105.0, lat - 35.0)
	radlat = lat / 180.0 * pi
	magic = math.sin(radlat)
	magic = 1 - ee * magic * magic
	sqrtmagic = math.sqrt(magic)
	dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
	dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
	mglat = lat + dlat
	mglng = lng + dlng
	return [mglng, mglat]


def gcj02towgs84(lng, lat):
	"""
	GCJ02(火星坐标系)转GPS84
	:param lng:火星坐标系的经度
	:param lat:火星坐标系纬度
	:return:
	"""
	if out_of_china(lng, lat):
		return lng, lat
	dlat = transformlat(lng - 105.0, lat - 35.0)
	dlng = transformlng(lng - 105.0, lat - 35.0)
	radlat = lat / 180.0 * pi
	magic = math.sin(radlat)
	magic = 1 - ee * magic * magic
	sqrtmagic = math.sqrt(magic)
	dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
	dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
	mglat = lat + dlat
	mglng = lng + dlng
	return [lng * 2 - mglng, lat * 2 - mglat]


def transformlat(lng, lat):
	ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
		  0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
	ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
			math.sin(2.0 * lng * pi)) * 2.0 / 3.0
	ret += (20.0 * math.sin(lat * pi) + 40.0 *
			math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
	ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
			math.sin(lat * pi / 30.0)) * 2.0 / 3.0
	return ret


def transformlng(lng, lat):
	ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
		  0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
	ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
			math.sin(2.0 * lng * pi)) * 2.0 / 3.0
	ret += (20.0 * math.sin(lng * pi) + 40.0 *
			math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
	ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
			math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
	return ret


def out_of_china(lng, lat):
	"""
	判断是否在国内，不在国内不做偏移
	:param lng:
	:param lat:
	:return:
	"""
	if lng < 72.004 or lng > 137.8347:
		return True
	if lat < 0.8293 or lat > 55.8271:
		return True
	return False


def sz2wgs84(lon, lat):
	"""
	深圳坐标转wgs84坐标
	:param lon:
	:param lat:
	:return:
	"""
	url = "http://192.168.37.134:8080/ConvertCoord/servlet/local2wgs"
	html = spider_util.open_url(url, data={'lat': lon, 'lon': lat})
	bsObj = BeautifulSoup(html, "html.parser", from_encoding="utf-8")
	zb = bsObj.get_text().strip()
	zb_arr = zb.split(',')
	lon = zb_arr[0]  # 经度坐标
	lat = zb_arr[1]
	time.sleep(0.1)  # 休眠1秒
	return [lon, lat]


def bd09towgs84(bd_lon, bd_lat):
	bd_lon, bd_lat = try_convert_float(bd_lon, bd_lat)
	zb_arr = bd09togcj02(bd_lon, bd_lat);
	return gcj02towgs84(zb_arr[0], zb_arr[1])


def try_convert_float(lon, lat):
	return float(lon), float(lat)


if __name__ == '__main__':
	lng = 128.543
	lat = 37.065
	result1 = gcj02tobd09(lng, lat)
	result2 = bd09togcj02(lng, lat)
	result3 = wgs84togcj02(lng, lat)
	result4 = gcj02towgs84(lng, lat)
	result5 = sz2wgs84(103708.20841, 15624.99613)
	hgzb = '114.05128002388166,22.517990291774773;114.05085974276022,' \
								'22.51643138601076;114.05143300314968,22.514016994146797;114.05165579232546,' \
								'22.512960264252026;114.05349178693803,22.50378784973348;114.05602264219532,' \
								'22.505833775670418;114.05651137152735,22.510384955045463;114.05805481291104,' \
								'22.512945690632126;114.0640855543873,22.517544762206928;114.06278432929155,' \
								'22.51964498193829;114.06196193829594,22.52004875468712;114.06096907763363,' \
								'22.520866387848155;114.05915188926225,22.519929545761002;114.0563208397546,' \
								'22.518711971127434;114.05123859795003,22.518027514234724;114.05128002388166,' \
								'22.517990291774773'
	points_in_polygon_list = hgzb.split(';')
	points_bd=[]
	for point in points_in_polygon_list:
		if not point:
			continue
		lon, lat = tuple(try_convert_float(*point.split(',')))
		gjc02arr=wgs84togcj02(lon, lat)
		data = gcj02tobd09(gjc02arr[0], gjc02arr[1])
		point_bd = ','.join(str(s) for s in data if s)
		points_bd.append(point_bd)
	polygon_bd_str = ';'.join(points_bd)  # 拼接转换坐标系后的学区范围坐标
	print(polygon_bd_str)