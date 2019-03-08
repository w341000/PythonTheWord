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
sql = 'SELECT a.table_name 表,a.column_name 字段,a.comments 字段中文名称,b.comments AS 表中文名称 FROM user_col_comments a JOIN  user_tab_comments  b ON a.table_name=b.table_name  WHERE a.table_name IN (SELECT table_name FROM user_tables)'
# oracle_db = create_engine('oracle+cx_oracle://wwyjfx:Fxyj#17W*2w@10.190.41.13:1521/?service_name=coreora')
oracle_db = create_engine('oracle+cx_oracle://wwyjfx:m123@localhost:1521/?service_name=orcl')

table_info = {}  # {'T_YW_ZZ_LD':'三小场所应用-楼栋信息列表接口'}
filed_info = {}  # {'T_YW_ZZ_LD':{'ID':'数据记录id','LDBM':'楼栋编码'}}


def get_table_comment():
	"""
	获取所有表及字段元数据信息 包含表中文名称，表英文名称，字段中文名称，字段英文名称
	:return:
	"""
	df = pandas.read_sql_query(sql, oracle_db)
	for index, row in df.iterrows():
		table = row['表']
		table_info[table] = row['表中文名称']  # 放入表中文名称及表英文名称
		fileds = filed_info.get(table)
		if not fileds:
			fileds = {}
			filed_info[table] = fileds
		fileds[row['字段']] = row['字段中文名称']  # 放入字段中文名称及字段英文名称


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
			sql_field = ''
			for field in this_filed_info.keys():
				sql_field = sql_field + 'count(' + field + ') ' + field + ','

			sql_field = sql_field[:-1]
			sql = 'select ' + sql_field + ' from ' + table
			df = pandas.read_sql_query(sql, oracle_db)
			sample_dataframe = get_sample_dataframe(table)  # 获取一行样例数据
			not_empty_sample_dataframe = try_get_not_empty_sample_dataframe(table)  # 取非空样例数据
			for field in this_filed_info.keys():
				data_item = {}
				f_count = df.get_value(0, field.lower())
				data_item['数据表'] = table
				data_item['数据表中文名称'] = table_info[table]
				data_item['字段编码'] = field
				data_item['字段中文'] = this_filed_info[field]
				percent = None
				if total is not 0:
					percent = f_count / total
					if math.isnan(percent):
						pass
					else:
						percent = str(round(percent * 100, 2)) + '%'
				data_item['总数据量'] = table_count
				data_item['字段非空数据量'] = str(f_count)
				data_item['字段非空所占比例'] = percent
				sample_data = None  # 样例数据
				if not sample_dataframe.empty:
					sample_data = sample_dataframe.at[0, field.lower()]
				data_item['样例数据一'] = sample_data
				not_empty_sample_data = None  # 非空样例数据
				if not not_empty_sample_dataframe.empty:
					not_empty_sample_data = not_empty_sample_dataframe.at[0, field.lower()]
				data_item['非空样例数据'] = not_empty_sample_data
				data.append(data_item)
		except Exception as e:

			print("发生异常信息:" + repr(e) + ' ,当前表:' + table + ',当前字段:' + field)
		print('完成表：' + table + ',' + str(round((idx + 1) / len(keys) * 100, 2)) + '%')
	return data


def get_sample_dataframe(table: str):
	"""
	获取前几行样例数据
	:param table:
	:return:
	"""
	sql = '(select a.*,ROWNUM RN from ' + table + ' a)'
	outer_sql = 'select * from ' + sql + ' where RN<=3'
	sample_dataframe = pandas.read_sql_query(outer_sql, oracle_db)  # .ix[[0]].values[0][0]
	# print(sample_dataframe.get_value(0,'address'))
	return sample_dataframe


def try_get_not_empty_sample_dataframe(table: str):
	"""
	尝试获取该表中该字段的非空值作为样例数据
	:param table: 
	:param field: 
	:return: 
	"""
	keys = filed_info[table].keys()
	innersql = 'select '
	for field in keys:
		innersql = innersql + ' max(' + field + ') ' + field + ' ,'
	innersql = innersql[:-1]
	innersql = innersql + ' from ' + table
	sample_dataframe = pandas.read_sql_query(innersql, oracle_db)
	return sample_dataframe


def main():
	# 获取cursor
	print('------------start-----------------')

	columns = ['字段编码', '字段中文', '字段非空数据量', '总数据量', '字段非空所占比例', '数据表', '数据表中文名称', '样例数据一', '非空样例数据']
	get_table_comment()
	data = get_table_count()
	directory = 'D:\\pythonresult\\'
	if not os.path.exists(directory):
		os.makedirs(directory)
	DataFrame(data).to_excel(os.path.join(directory, "数据字典" + now_date + ".xls"), columns=columns, index=False)
	print('--------------end----------------')


if __name__ == '__main__':
	main()
# get_table_comment()
# try_get_not_empty_sample_dataframe('OPENDATA_ZCBZF_XQJBXX')
