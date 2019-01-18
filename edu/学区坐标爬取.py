# -*- coding: utf-8 -*-
from util import spider_util
from bs4 import BeautifulSoup
import json
import demjson
from pandas import DataFrame
from util import coordinate_util


def areaSnatch():
	"""
	抓取小学学区图位置信息
	:return:
	"""
	# 小学学区
	datas = []
	primaryschool_url = 'http://map.28dat.net/inc/ftxx.js'
	data = spider_util.open_url(primaryschool_url).decode()
	start = data.find('return')
	end = data.find('];')
	data = data[start + 6:end + 1]  # 获取其中坐标信息
	primaryschool_area = demjson.decode(data)
	coordinate_handle(primaryschool_area, '小学')
	# 初中学区
	middleschool_url = 'http://map.28dat.net/inc/ftcz.js'
	data = spider_util.open_url(middleschool_url).decode()
	start = data.find('return')
	end = data.find('];')
	data = data[start + 6:end + 1]  # 获取其中坐标信息
	middleschool_area = demjson.decode(data)
	coordinate_handle(middleschool_area, '初中')
	datas.extend(primaryschool_area)
	datas.extend(middleschool_area)
	return datas


def requset_school_info(areas):
	schoolnames = []
	infourl_prefix = 'http://map.28dat.net/s_ft/school.aspx?no='
	for school in areas:
		print(school)
		schoolnames.append(school['name'])
		resulet = spider_util.open_url(infourl_prefix + '1' + school['no'])
		bsObj = BeautifulSoup(resulet, "html.parser", from_encoding="utf-8")
		text = bsObj.select_one('#s_desc').get_text()
		print(text)
	print(schoolnames)


def coordinate_handle(areas, schooltype: int):
	"""
	学区信息解析处理
	:param schooltype:
	:param areas:
	:return:
	"""
	for school in areas:
		point = school['point']  # 百度坐标字符串
		bd_lon, bd_lat = coordinate_util.try_convert_float(*tuple(point.split(',')))
		lon_84, lat_84 = tuple(coordinate_util.bd09towgs84(bd_lon, bd_lat))
		school['bd_lon'] = bd_lon
		school['bd_lat'] = bd_lat
		school['lon_84'] = lon_84
		school['lat_84'] = lat_84
		school['schooltype'] = schooltype
		if school['name'] == '水围小学':
			school[
				'polygon'] = '114.0633,22.534045;114.0634,22.52855;114.0628,22.521258;114.067507,22.521794;114.070507,' \
							 '22.522794;114.072412,22.524113;114.074029,22.525699;114.0746,22.527468;114.0746,' \
							 '22.5288;114.07106,22.5287;114.069627,22.5342 '
		if school['name'] == '皇岗中学':
			school['polygon'] = '114.06335630432059,22.53407055006403;114.0633570352742,' \
								'22.52892505079072;114.06346863640744,22.528256298155046;114.06333038826526,' \
								'22.526891409780625;114.06318181142706,22.5246178427583;114.0630325230082,' \
								'22.522394809728347;114.0629434046132,22.521333587742063;114.06877342108848,' \
								'22.522389967130895;114.07232486225952,22.524357038565782;114.0730238399688,' \
								'22.524157289190093;114.07402998731851,22.523322509788134;114.07466511847029,' \
								'22.52267052672166;114.0759830451113,22.520432070153596;114.08186917875757,' \
								'22.52170881191117;114.08102355412635,22.524914183231346;114.08252321508871,' \
								'22.52897097054742;114.07943882066171,22.52999201450642;114.07946277559604,' \
								'22.532391529886656;114.07942632794372,22.53438421673346;114.06335630432059,' \
								'22.53407055006403 '
		if school['name'] == '福田外国语学校南校区初中部（暂定名）':
			school['polygon'] = '114.0629360257067,22.520920473399144;114.0625158974266,' \
								'22.519362397148825;114.06309218401087,22.516947467537996;114.06331627482768,' \
								'22.515890636312466;114.06516390653805,22.50671939281994;114.0676961580645,' \
								'22.508769379251227;114.06818119507018,22.513321296078516;114.06972362173309,' \
								'22.515887848366944;114.07575038062822,22.52053043740426;114.0744486351297,' \
								'22.522618348565825;114.07362632561198,22.52301515156071;114.07263319972233,' \
								'22.523825098839897;114.0708162964302,22.522876576538774;114.06798413768293,' \
								'22.521646582687115;114.06289448830186,22.520957749246804;114.0629360257067,' \
								'22.520920473399144 '
		polygon = school['polygon']
		if not polygon:
			school['polygon_84'] = None
			continue
		points_in_polygon_list = polygon.split(';')
		points_wgs84 = []
		for point_bd in points_in_polygon_list:
			if point_bd is None or point_bd == '':
				continue
			lon, lat = tuple(coordinate_util.try_convert_float(*point_bd.split(',')))
			data = coordinate_util.bd09towgs84(lon, lat)
			point_wgs84 = ','.join(str(s) for s in data if s)
			points_wgs84.append(point_wgs84)
		points_wgs84.append(points_wgs84[0])  # 为了保证头尾相连，添加第一个坐标到末尾
		polygon_wgs84_str = ';'.join(points_wgs84)  # 拼接转换坐标系后的学区范围坐标
		school['polygon_84'] = polygon_wgs84_str


def main():
	datas = areaSnatch()
	DataFrame(datas).to_excel('D:\\pypy\\pythonresult\\edu\\学区信息.xls', index=False)
	DataFrame(datas).to_json('D:\\pypy\\pythonresult\\edu\\学区信息.json', orient='records', force_ascii=False)


if __name__ == '__main__':
	main()
