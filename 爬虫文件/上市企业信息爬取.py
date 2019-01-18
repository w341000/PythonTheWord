# -*- coding: utf-8 -*-
from util import spider_util
import demjson
from pandas import DataFrame


def doRequest(datas=[], stockType=''):
	"""
	请求http://s.askci.com/StockInfo/StockList/GetList，抓取上市企业信息
	:param datas: 保存数据的数组
	:param stockType: 股票类型，A股：a,港股：hk,新三板：xsb
	:return:
	"""
	url = 'http://s.askci.com/StockInfo/StockList/GetList?pageNum={pageNum}&stockType={stockType}'
	pageNum = 1
	typestr = stockType
	if stockType is None or stockType == '':
		typestr = '所有类型'
	while True:
		print(f'抓取上市企业信息，当前第：{pageNum}页,股票类型为{typestr}')
		url = url.format(pageNum=pageNum, stockType=stockType)
		result = spider_util.open_url(url)
		json = demjson.decode(result)
		data = json['data']
		if data is None or len(data) == 0:
			break
		if pageNum > json['totalPageNum']:
			break
		for obj in data:
			obj['stockType'] = stockType
		datas.extend(data)
		pageNum += 1
	return datas


if __name__ == '__main__':
	datas = []
	doRequest(datas, stockType='a')
	doRequest(datas, stockType='hk')
	doRequest(datas, stockType='xsb')
	df = DataFrame(datas)
	df.to_csv('D:\\pypy\\pythonresult\\上市企业\\上市企业信息.csv')
