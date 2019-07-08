# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from pandas import DataFrame
from util import spider_util
import util
from util.redis_util import RedisUtil

oracle_db = create_engine('oracle+cx_oracle://wwyjfx:m123@localhost:1521/?service_name=orcl')
redis_job_index = 'python:spider:jobspider:index'
redis_job_set = 'python:spider:joburls'


def get_list():
	data = []
	r = RedisUtil().get_redis_instance()
	for i in range(1, 2000):
		url = 'https://search.51job.com/list/040000,000000,0000,00,9,99,%2520,2,{page}.html?lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare='.format(
			page=i)
		# head = ['职位名', '公司名', '工作地点', '薪资', '发布时间', '职位详细URL']
		bsobj = spider_util.open_url_return_bsobj(url)
		div_tags = bsobj.select('#resultList .el')[1:]
		for div in div_tags:
			job = div.select_one('a').get_text().strip()
			job_url = div.select_one('a').get('href')
			redis_result = r.sadd(redis_job_set, job_url)
			if redis_result == 0:  # 结果为0，则添加失败，说明已经有该职位url信息
				continue
			company = div.select_one('.t2 a').get_text().strip()
			address = div.select_one('.t3').get_text().strip()
			salary = div.select_one('.t4').get_text().strip()
			money_toplimit = None
			money_lowerlimit = None
			money_unit = None
			time_unit = None
			if '/' in salary:
				money_range = salary.split('/')[0]
				money_unit = money_range[-1]
				money_range = money_range[:-1]
				money_toplimit = money_range
				money_lowerlimit = money_range
				if '-' in money_range:  # 分割薪水上下限
					money_lowerlimit = money_range.split('-')[0]
					money_toplimit = money_range.split('-')[1]
				time_unit = salary.split('/')[1]
			push_time = div.select_one('.t5').get_text().strip()
			item = {'职位名': job, '公司名': company, '工作地点': address, '薪资': salary, '发布时间': push_time, '职位详细URL': job_url,
					'金额上限': money_toplimit, '金额下限': money_lowerlimit, '时间单位': time_unit, '金额单位': money_unit}
			data.append(item)
		spider_util.log_progress(i,2000,start_from_zero=False)

	return DataFrame(data)


def urllist_handle():
	pass


def main():
	df = get_list()
	print(df)


if __name__ == '__main__':
	main()
