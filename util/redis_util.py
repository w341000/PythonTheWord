# -*- coding: utf-8 -*-
import redis

class RedisUtil:

	def __init__(self, host= '127.0.0.1', port=6379, password='', decode_responses=True):
		self.pool = redis.ConnectionPool(host=host,port=port,password=password, decode_responses=True)

	def get_redis_instance(self):
		"""
		获取一个redis实例
		:return:
		"""
		return redis.Redis(connection_pool=self.pool)

