# -*- coding: utf-8 -*-
from util import db_util
from util import address_standardization
from util import spider_util
import math
def address_format(table,lonField,latField):
	sql="select * from "+table
	delete_sql="delete from "+table
	df=db_util.execute2Dataframe(sql)
	length=len(df)
	for i in range(length):
		lon=df.at[i,lonField]
		lat = df.at[i, latField]
		lon=float(lon)
		lat=float(lat)
		if lon is None or lon == '' or math.isnan(lon):
			continue
		addressComponent=address_standardization.location2normaladdress(lon,lat,coordtype='gcj02ll')
		street=addressComponent['town']
		df.at[i, 'STREET']=street
		spider_util.log_progress(i,length,detailedLog=True)
	# db_util.delete(delete_sql)
	df.to_csv('C:\\Users\\admin\\Desktop\\'+table+'.csv',index=False,sep=',')
	# df.to_sql(table,db_util.getSqlalchemyEngine(),if_exists='append',index=False)




#address_format("ZT_AQSC_QYYH_GIS","RT_LOG","RT_LAT")
#address_format("SWJC.MONITOR_STATION","COORX","COORY")
# address_format("lhsf.ST_STBPRP_B","LGTD","LTTD")
# address_format("lhsf.RS_INFO_B","LGTD","LTTD")
# address_format("LHSF.TB1501_MEIDSCIN_044","LGTD","LTTD")
address_format("YJZH_YJZJ","GCJLON","GCJLAT") #没有经纬度
# address_format("SPJK.MONITOR_DATA","GCJLON","GCJLAT")