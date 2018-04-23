# -*- coding: UTF-8 -*-
import re
import os
import time
from urllib import request,parse
import socket

# 检查ip是否可联通
def checkip(ip):
	# socket.setdefaulttimeout(3)
	proxy_host = "http://" + ip
	proxy = {"http":proxy_host}
	# 用这个网页去验证，遇到不可用ip会抛异常
	url = "http://ip.chinaz.com/getip.aspx"
	try:
		# 代理配置
		proxy_obj = request.ProxyHandler(proxy)
		opener = request.build_opener(proxy_obj)
		#验证代理，5秒超时
		res = opener.open(url,timeout=3).read()
		return True
	except Exception:
			#不可用打印
		return False


# 响应头
headers = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
    'Hosts': 'hm.baidu.com',
    'Referer': 'http://www.xicidaili.com/nn',
    'Connection': 'keep-alive'
}
for i in range(1,1000):
    url="http://www.xicidaili.com/wt/{}".format(i)
    print(url)
    req = request.Request(url=url,headers=headers)
    try:
        req = request.urlopen(req,timeout=3).read()
    except Exception:
        print("异常！")
        continue
    req = req.decode("utf-8")
    # 提取ip和端口
    ip_list = re.findall("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*?(\d{2,6})", req, re.S)
    # 将提取的ip和端口写入文件
    f = open("ip.txt","a+")
    for li in ip_list:
        ip = li[0] + ':' + li[1] + '\n'
        # if checkip(ip):
        f.write(ip.strip()+"\n")
    time.sleep(2)       # 每爬取一页暂停两秒