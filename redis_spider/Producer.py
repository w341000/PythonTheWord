# -*- coding: utf-8 -*-
from util import spider_util
from util.redis_util import RedisUtil


class Producer:

	def __init__(self, redis_prefix: str, host='127.0.0.1', port=6379, password='', decode_responses=True):
		self.redis_prefix = redis_prefix
		self.data = []
		self.redis_instance = RedisUtil(host, port, password, decode_responses).get_redis_instance()

	def request_by_urllib(self, url: str, func, self_rotation=5, timeout=5, data=None, from_encoding="utf-8"):
		"""
		使用urllib请求连接获取数据，并调用自定义函数处理数据
		:param url:
		:param func:
		:param self_rotation:
		:param timeout:
		:param data:
		:param from_encoding:
		:return:
		"""
		result = spider_util.open_url_return_bsobj(url, self_rotation, timeout, data, from_encoding)
		self.data.append(func(result))

	def save_data2redis_Set(self):
		"""
		将持有的资源数组保存进redis中的set，资源将被调用str()方法后保存
		:return:
		"""
		print('进行保存数据至redis中')
		for item in self.data:
			if item is None:
				continue
			self.redis_instance.sadd(self.redis_prefix, str(item))

	def clean(self):
		"""
		当前持有的资源数组清空，通常在多次循环保存时调用该方法
		:return:
		"""
		self.data = []


def get_data(bsObj):
	print(bsObj)
	return bsObj


if __name__ == '__main__':
	p = Producer('python:spider:producer')
	url = 'http://demo.audaque.com:8082/screen2/'
	p.request_by_urllib(url, get_data)
	p.save_data2redis()
