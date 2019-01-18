# -*- coding: utf-8 -*-

import cx_Oracle as cx
import sqlalchemy
import pandas
from sqlalchemy import create_engine
import os
import math
from pandas import  DataFrame

table_count=[]
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
sql='select a.table_name 表,a.column_name 字段,a.comments 字段中文名称,b.comments as 表中文名称 from user_col_comments a join  user_tab_comments  b on a.table_name=b.table_name  where a.table_name in (select table_name from user_tables) '
oracle_db = create_engine('oracle+cx_oracle://wwyjfx:m123@localhost:1521/?service_name=orcl')

def getTableCount(row):
	try:
		table=row['表']
		field=row['字段']
		f_cn=row['字段中文名称']
		t_cn=row['表中文名称']
		total=pandas.read_sql_query('select count(*) from '+table, oracle_db).ix[[0]].values[0][0]
		f_count = pandas.read_sql_query('select count('+field+') from ' + table, oracle_db).ix[[0]].values[0][0]
		percent=f_count/total
		if math.isnan(percent):
			pass
		else:
			percent=str(percent*100)+'%'
		field_obj={'表':table,'字段':field,'字段中文名称':f_cn,'表中文名称':t_cn,'字段数据量':f_count,'总数据量':total,'所占比例':percent}
		table_count.append(field_obj)
	except Exception as e:
		print("发生异常信息:"+repr(e)+' ,当前表:'+table+',当前字段:'+field)

#获取cursor
df=pandas.read_sql_query(sql, oracle_db)
df.apply(getTableCount,axis =1)
DataFrame(table_count).to_excel()
DataFrame(table_count).to_csv("D:\\011111111111111111111111\\00临时文件\\table_count.csv",
										index=False,
										sep=',')
