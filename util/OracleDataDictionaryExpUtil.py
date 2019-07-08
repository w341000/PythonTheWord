# -*- coding: utf-8 -*-
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
sql = """
SELECT
	a.table_name,
	a.column_name,
	a.comments AS column_comments,
	b.comments AS table_comments ,
	c.data_type,
	c.data_length,
	c.nullable,
	c.data_default
FROM
	user_col_comments a
	LEFT JOIN user_tab_comments b ON a.table_name = b.table_name 
	LEFT JOIN user_tab_columns c ON a.table_name=c.table_name AND a.column_name=c.column_name
WHERE
	b.table_type='TABLE'
  
"""

table_list_sql = """
SELECT table_name,table_type,comments AS table_comments 
FROM user_tab_comments
WHERE table_type='TABLE'
"""
# oracle_db = create_engine('oracle+cx_oracle://wwyjfx:Fxyj#17W*2w@10.190.41.13:1521/?service_name=coreora')
oracle_db = create_engine('oracle+cx_oracle://lhdm:lhdm#gov@10.169.11.13:1521/?service_name=orcl')
table_list_df = pandas.read_sql(table_list_sql, oracle_db)
field_df = pandas.read_sql_query(sql, oracle_db)


def get_table_count():
	"""
	获取所有表及字段数量统计
	:return:
	"""
	data = []
	table_length = len(table_list_df)
	for table_index, table_row in table_list_df.iterrows():
		try:
			table = table_row['table_name']
			table_comments = table_row['table_comments']
			table_count = pandas.read_sql_query('select count(*) from ' + table, oracle_db).ix[[0]].values[0][0]

			this_field_df = field_df[field_df.table_name == table]
			sql_field = ''
			for tmp_idx, field_row in this_field_df.iterrows():
				field = field_row['column_name']
				data_type = field_row['data_type']
				if data_type == 'CLOB' or data_type == 'BLOB':
					continue
				sql_field = sql_field + 'count(' + field + ') ' + field + ','

			sql_field = sql_field[:-1]
			sql = 'select ' + sql_field + ' from ' + table
			df = pandas.read_sql_query(sql, oracle_db)
			sample_dataframe = get_sample_dataframe(table)  # 获取一行样例数据
			not_empty_sample_dataframe = try_get_not_empty_sample_dataframe(this_field_df, table)  # 取非空样例数据
			for field_index, field_row in this_field_df.iterrows():
				field_name = field_row['column_name']
				data_type = field_row['data_type']
				data_item = {}
				f_count = int(df.get(field_name.lower(), 0))
				data_item['数据表'] = table
				data_item['数据表中文名称'] = table_comments
				data_item['字段编码'] = field_name
				data_item['字段中文'] = field_row['column_comments']
				data_item['字段类型'] = data_type
				data_item['字段长度'] = field_row['data_length']
				data_item['能否为空'] = field_row['nullable']
				data_item['默认值'] = field_row['data_default']
				percent = None
				if table_count is not 0:
					percent = f_count / table_count
					if math.isnan(percent):
						pass
					else:
						percent = str(round(percent * 100, 2)) + '%'
				data_item['总数据量'] = table_count
				data_item['字段非空数据量'] = str(f_count)
				data_item['字段非空所占比例'] = percent
				if data_type != 'CLOB' and data_type != 'BLOB' and data_type != 'RAW':
					sample_data = None  # 样例数据
					if not sample_dataframe.empty:
						sample_data = sample_dataframe.at[0, field_name.lower()]
					data_item['样例数据一'] = sample_data
					not_empty_sample_data = None  # 非空样例数据
					if not not_empty_sample_dataframe.empty:
						not_empty_sample_data = not_empty_sample_dataframe.at[0, field_name.lower()]
					data_item['非空样例数据'] = not_empty_sample_data
				data.append(data_item)
		except Exception as e:

			print("发生异常信息:" + repr(e) + ' ,当前表:' + table + ',当前字段:' + field)
		print('完成表：' + table + ',' + str(round((table_index + 1) / table_length * 100, 2)) + '%')
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


def try_get_not_empty_sample_dataframe(this_field_df: DataFrame, table):
	"""
	尝试获取该表中该字段的非空值作为样例数据
	:param table: 
	:param field: 
	:return: 
	"""
	innersql = 'select  '
	for index, row in this_field_df.iterrows():
		field = row['column_name']
		data_type = row['data_type']
		if data_type == 'CLOB' or data_type == 'BLOB':
			continue
		innersql = innersql + ' max(' + field + ') ' + field + ' ,'
	innersql = innersql[:-1]
	innersql = innersql + ' from ' + table
	sample_dataframe = pandas.read_sql_query(innersql, oracle_db)
	return sample_dataframe


def main():
	# 获取cursor
	print('------------start-----------------')

	columns = ['字段编码', '字段中文', '字段类型', '字段长度', '字段非空数据量', '总数据量', '字段非空所占比例', '数据表', '数据表中文名称', '能否为空', '默认值', '样例数据一',
			   '非空样例数据']
	data = get_table_count()
	directory = 'D:\\pythonresult\\'
	if not os.path.exists(directory):
		os.makedirs(directory)
	DataFrame(data).to_excel(os.path.join(directory, "罗湖项目精细化数据字典" + now_date + ".xlsx"), columns=columns, index=False,
							 encoding='utf-8')
	print('--------------end----------------')


if __name__ == '__main__':
	main()
