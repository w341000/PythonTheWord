# -*- coding: utf-8 -*-
from collections import Iterable
import time, functools
# print(product(1, 2, 5, 6))


# print(str=="123")
from functools import reduce

'''
def findMinAndMax(list):
    min = None
    max = None
    for value in list:
        if max is None or value > max:
            max = value
        if min is None or value < min:
            min = value
    return min, max


if findMinAndMax([]) != (None, None):
    print('测试失败!')
elif findMinAndMax([7]) != (7, 7):
    print('测试失败!')
elif findMinAndMax([7, 1]) != (1, 7):
    print('测试失败!')
elif findMinAndMax([7, 1, 3, 9, 5]) != (1, 9):
    print('测试失败!')
else:
    print('测试成功!')
'''

'''
def count():
	fs = []
	for i in range(1, 4):
		def f():
			return i * i

		fs.append(f)
	return fs


f1, f2, f3 = count()
'''

def metric(fn):
    print('%s executed in %s ms' % (fn.__name__, 10.24))
	functools.partial(int, base=2)
    return fn

