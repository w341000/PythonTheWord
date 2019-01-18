# -*- coding: utf-8 -*-\
from bs4 import BeautifulSoup
from pandas import DataFrame

from util import spider_util

url='http://192.168.37.134:8080/ConvertCoord/servlet/wgs2local'
# wgs84转换坐标为深圳坐标
paths=[
    'D:/福田决策文件/消防数据表/消防数据/T_XF_XIAOFANG_BUWEI.csv',
'D:/福田决策文件/消防数据表/消防数据/T_XF_SCHSELFCHECKRECORD.csv',
'D:/福田决策文件/消防数据表/消防数据/T_XF_INSRECORD.csv'
]
for path in paths:
    datas,heads= spider_util.readCSV2List(path)
    for data in datas:
        jd84=data['jd84']
        wd84=data['wd84']
        #print(jd84+'-----'+wd84)
        html= spider_util.open_url(url, data={'lat':jd84, 'lon':wd84})
        bsObj = BeautifulSoup(html, "html.parser", from_encoding="utf-8")
        zb=bsObj.get_text().strip()
        zb_arr=zb.split(',')
        lon=zb_arr[0]#经度坐标
        lat=zb_arr[1]
        data['lon']=lon
        data['lat']=lat
    DataFrame(datas).to_csv(path, index=False, sep=',')



