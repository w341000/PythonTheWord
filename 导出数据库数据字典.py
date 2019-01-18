import pandas
from sqlalchemy import create_engine
import os
import math
from pandas import DataFrame
import datetime

now_time = datetime.datetime.now()
now_date = now_time.strftime('%Y-%m-%d')
table_count = []
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
sql = 'select a.table_name 表,a.column_name 字段,a.comments 字段中文名称,b.comments as 表中文名称 from user_col_comments a join  user_tab_comments  b on a.table_name=b.table_name  where a.table_name in (select table_name from user_tables)'
# oracle_db = create_engine('oracle+cx_oracle://wwyjfx:Fxyj#17W*2w@10.190.41.13:1521/?service_name=coreora')
oracle_db = create_engine('oracle+cx_oracle://wwyjfx:m123@localhost:1521/?service_name=orcl')


def getTableCount(row):
	try:
		table = row['表']
		field = row['字段']
		f_cn = row['字段中文名称']
		t_cn = row['表中文名称']
		f_count = None
		total = None
		percent = None
		total = pandas.read_sql_query('select count(*) from ' + table, oracle_db).ix[[0]].values[0][0]
		f_count = pandas.read_sql_query('select count(' + field + ') from ' + table, oracle_db).ix[[0]].values[0][0]
		percent = f_count / total
		if math.isnan(percent):
			pass
		else:
			percent = str(percent * 100) + '%'
	except Exception as e:
		print("发生异常信息:" + repr(e) + ' ,当前表:' + table + ',当前字段:' + field)
	field_obj = {'表': table, '字段': field, '字段中文名称': f_cn, '表中文名称': t_cn, '字段数据量': f_count, '总数据量': total,
				 '所占比例': percent}
	table_count.append(field_obj)


table_info = {}
filed_info = {}
# 获取cursor
print('------------start-----------------')


def get_table_comment():
	"""
	获取所有表及字段注释
	:return:
	"""
	df = pandas.read_sql_query(sql, oracle_db)
	for index, row in df.iterrows():
		table = row['表']
		table_info[table] = row['表中文名称']  # 放入表注释信息
		fileds = filed_info.get(table)
		if not fileds:
			fileds = {}
			filed_info[table] = fileds
		fileds[row['字段']] = row['字段中文名称']  # 放入字段注释


def get_table_count():
	"""
	获取所有表及字段数量统计
	:return:
	"""
	data = []
	keys = table_info.keys()
	for idx, table in enumerate(keys):
		try:
			table_count = total = pandas.read_sql_query('select count(*) from ' + table, oracle_db).ix[[0]].values[0][0]
			this_filed_info = filed_info[table]
			sql = 'select '
			sql_field = ''
			for field in this_filed_info.keys():
				sql_field = sql_field + 'count(' + field + ') ' + field + ','

			sql_field = sql_field[:-1]
			sql = 'select ' + sql_field + ' from ' + table
			df = pandas.read_sql_query(sql, oracle_db)
			for field in this_filed_info.keys():
				data_item = {}
				f_count = df.get_value(0, field.lower())
				data_item['数据表'] = table
				data_item['表注释'] = table_info[table]
				data_item['字段'] = field
				data_item['字段注释'] = this_filed_info[field]
				percent = None
				percent = f_count / total
				if math.isnan(percent):
					pass
				else:
					percent = str(percent * 100) + '%'
				data_item['总数据量'] = table_count
				data_item['字段数据量'] = str(f_count)
				data_item['所占比例'] = percent
				data.append(data_item)
		except Exception as e:
			print("发生异常信息:" + str(e) + ' ,当前表:' + table + ',当前字段:' + field)
		print('完成表：' + table + ',' + str(round((idx + 1) / len(keys) * 100, 2)) + '%')
	return data


columns = ['字段', '字段注释', '字段数据量', '总数据量', '所占比例', '数据表', '表注释']
get_table_comment()
data = get_table_count()
DataFrame(data).to_excel("D:\\pythonresult\\数据字典" + now_date + ".xls", columns=columns, index=False)
print('--------------end----------------')
