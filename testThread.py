# -*- coding: UTF-8 -*-
from urllib import request
from random import choice

# 从文本文件中按行读取ip代理信息
def get_proxyip_pool(file):
	with open(file) as inf:
		lines = inf.readlines()
		proxys = []
		for i in range(0, len(lines)):
			proxy_host = "http://" + lines[i]
			proxy_temp = {"http": proxy_host}
			proxys.append(proxy_temp)
		return proxys

if __name__ == "__main__":
    #访问网址
    url = 'https://www.szcredit.org.cn/web/GSPT/newGSPTDetail3.aspx?ID=0433e37333c44d14a56af16b7aaf153e'
    main_url='http://www.whatismyip.com.tw/'
    # proxys = get_proxyip_pool('D:\\可用ip.txt')
    proxy={'http':'203.174.112.13:3128'}
    #创建ProxyHandler 60.177.277.182:18118
    headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
    req = request.Request(url=url, data=None, headers=headers)
    proxy_support = request.ProxyHandler(proxy)
    #创建Opener
    opener = request.build_opener(proxy_support)
    #添加User Angent
    opener.addheaders = [('User-Agent','Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36')]
    #安装OPener
    #request.install_opener(opener)
    #使用自己安装好的Opener
    response = request.urlopen(req,timeout=10)
    #读取相应信息并解码
    html = response.read().decode("gb18030")
    #打印信息
    print(html)