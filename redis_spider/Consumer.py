# -*- coding: utf-8 -*-
from util import spider_util
from util.redis_util import RedisUtil


class Consumer:
	def __init__(self, redis_prefix: str, host='127.0.0.1', port=6379, password='', decode_responses=True):
		self.redis_prefix = redis_prefix
		self.data = []
		self.redis_instance = RedisUtil(host, port, password, decode_responses).get_redis_instance()

	def open(self, url: str, func, self_rotation=5, timeout=5, data=None, from_encoding="utf-8"):
		result = spider_util.open_url_return_bsobj(url, self_rotation, timeout, data, from_encoding)
		return func(result)

	def open_from_redis(self, func, storage_size=0, self_rotation=5, timeout=5, data=None, from_encoding="utf-8"):
		"""

		:param func: 对请求到的数据进行处理的函数
		:param storage_size:
		:param self_rotation:自旋重试次数
		:param timeout: 连接超时时间 默认值5秒
		:param data:
		:param from_encoding: 返回数据的编码格式，默认为utf-8
		:return:
		"""
		url = self.redis_instance.spop(self.redis_prefix)
		return self.open(url, self_rotation, timeout, data, from_encoding)
