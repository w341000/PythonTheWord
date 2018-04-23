# -*- coding: utf-8 -*-
from urllib import request
from queue import Queue
from threading import Thread
from queue import Empty


def do_checkip(q,valid_ips,timeout):
	# 用这个网页去验证，遇到不可用ip会抛异常
	url = "http://ip.chinaz.com/getip.aspx"
	headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
	values = {}  # post请求携带的参数
	# 深圳信用网信用风险提示url
	main_url = 'https://www.szcredit.org.cn/web/GSPT/CreditRiskList.aspx'
	req = request.Request(url=url, data=None, headers=headers)
	print('线程开始执行检查ip联通动作')
	while True:
		try:
			proxy=q.get(block=False)#从队列获取ip
			# 代理配置
			proxy_obj = request.ProxyHandler(proxy)
			opener = request.build_opener(proxy_obj)
			# 验证代理，timeout秒超时
			res = opener.open(req,timeout=timeout).read()
			valid_ip = proxy['http'][7:]
			print('有效ip:{} '.format(valid_ip))
			valid_ips.put(valid_ip)
			q.task_done()
		except Empty:
			print('线程执行完毕,退出该线程')
			break
		except Exception:
			#不可用打印
			print("不可用：{}".format(proxy))
			q.task_done()
			continue


def checkip():
	num=20
	inf = open("d:\\ip.txt")    # 这里打开刚才存ip的文件
	lines = inf.readlines()
	proxys = Queue()
	for i in range(0,len(lines)):
		proxy_host = "http://" + lines[i]
		proxy_temp = {"http":proxy_host}
		proxys.put(proxy_temp)#将txt文件中的所有ip放入进去
	# 将可用ip写入valid_ip.txt
	valid_ips= Queue()
	# fork NUM个线程等待队列
	for i in range(num):
		t = Thread(target=do_checkip,args=(proxys,valid_ips,5))
		t.setDaemon(True)
		t.start()
	print('主线程等待检查线程的执行')
	proxys.join()
	print('检查完毕,开始写入文本')
	with open("d:\\可用ip.txt", "w" ) as f1:
		while True:
			try:
				ip=valid_ips.get(block=False)
				f1.write(ip)
			except Empty:
				break

checkip()


