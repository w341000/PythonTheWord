# -*- coding: utf-8 -*-
from util import spider_util,coordinate_util
import json
import time

def address2location(address='', city='深圳市', ret_coordtype='bd09ll', ak='Exhb17fjBe4YoCCERO0mAkRsnTXDRpzN'):

	"""
	地址解析为百度经纬度坐标信息
	:param address: 需要被解析的地址
	:param city: 地址所在城市，默认深圳市
	:param ret_coordtype: 坐标系，默认bd09ll（百度经纬度坐标），可选gcj02ll（国测局坐标）
	:param sn:百度校验码
	:return:
	"""
	time.sleep(0.00625)
	url = 'http://api.map.baidu.com/geocoder/v2/'
	params = {'address': address, 'output': 'json', 'city': city, 'ret_coordtype': ret_coordtype,
			  'ak': ak}
	response = spider_util.open_url(url, data=params)
	data = json.loads(response)
	status = data['status']
	if status is not 0:
		msg = data['msg']
		raise RuntimeError('地址解析失败\n错误代码：' + str(status) + '\n原因：' + str(msg))
	location = data.get('result').get('location')
	lng = location['lng']
	lat = location['lat']
	return lng, lat


def location2normaladdress(lng, lat, coordtype='bd09ll', ret_coordtype='bd09ll',
						   ak='Exhb17fjBe4YoCCERO0mAkRsnTXDRpzN', ):
	"""
	:param lng: 经度
	:param lat: 纬度
	:param coordtype: 坐标的类型，目前支持的坐标类型包括：

			bd09ll（百度经纬度坐标）、bd09mc（百度米制坐标）、gcj02ll（国测局坐标）、wgs84ll（ GPS经纬度）

	:param ret_coordtype: 返回的坐标类型:

	 gcj02ll（国测局坐标）、默认bd09ll（百度经纬度坐标）

	:param ak: 百度校验码
	:return: 返回addressComponent字典，包含以下信息
	country 国家

	province 省名

	city 城市名

	district 区县名

	town	乡镇名(对于地级市对应街道名称)

	street 街道名（行政区划中的街道层级）

	street_number 街道门牌号

	adcode 行政区划代码

	country_code 国家代码

	direction 相对当前坐标点的方向，当有门牌号的时候返回数据

	distance 相对当前坐标点的距离，当有门牌号的时候返回数据

	bd_x 百度坐标经度

	bd_y 百度坐标纬度

	lon84 84坐标经度

	lat84 84坐标纬度

	formatted_address 格式化后的地址
	"""
	time.sleep(0.00625)
	url = 'http://api.map.baidu.com/geocoder/v2/'
	params = {'location': str(lat) + ',' + str(lng), 'output': 'json', 'ret_coordtype': ret_coordtype,
			  'ak': ak, 'coordtype': coordtype, 'extensions_town': 'true', 'latest_admin': '1',
			  'extensions_poi': 'null'}
	response = spider_util.open_url(url, data=params)
	data = json.loads(response)
	result = data['result']
	status = data['status']
	if status is not 0:
		msg = data['msg']
		raise RuntimeError('地址解析失败\n错误代码：' + str(status) + '\n原因：' + str(msg))
	formatted_address = result['formatted_address']
	addressComponent = result['addressComponent']
	addressComponent['bd_x']=lng
	addressComponent['bd_y']=lat
	lon84,lat84=coordinate_util.bd09towgs84(lng,lat)
	addressComponent['lon84'] = lon84
	addressComponent['lat84'] = lat84
	addressComponent['formatted_address']=formatted_address
	return addressComponent


def formatAddress(address):
	"""
	格式化地址，返回包含标准地址的字典，具体信息参考 location2normaladdress 的说明

	:param address:	需要被标准化的地址
	:return: 返回addressComponent字典，包含以下信息
	country 国家

	province 省名

	city 城市名

	district 区县名

	town	乡镇名(对于地级市对应街道名称)

	street 街道名（行政区划中的街道层级）

	street_number 街道门牌号

	adcode 行政区划代码

	country_code 国家代码

	direction 相对当前坐标点的方向，当有门牌号的时候返回数据

	distance 相对当前坐标点的距离，当有门牌号的时候返回数据

	bd_x 百度坐标经度

	bd_y 百度坐标纬度

	lon84 84坐标经度

	lat84 84坐标纬度

	formatted_address 格式化后的地址
	"""
	lng,lat = address2location(address)
	return location2normaladdress(lng,lat)


def main():
	lng, lat = address2location('福田区桂花路南红树福苑')
	data = location2normaladdress(lng, lat)
	print(data)


if __name__ == "__main__":
	main()
