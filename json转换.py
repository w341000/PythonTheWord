# -*- coding: utf-8 -*-
import json
import pandas as pd
from pandas import DataFrame
def readjson(filename,outfilename):
	with open(filename, "r", encoding='utf-8', newline='') as file:
		data=json.load(file)
		df=DataFrame(data)
		df.to_excel(outfilename,index=False)
		print(data)


# readjson("d://小学学区信息.json","d://小学学区信息.xls")

readjson("d://初中学区信息.json","d://初中学区信息.xls")




