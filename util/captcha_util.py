# -*- coding: utf-8 -*-
from capt import train
"""
光学识别验证码工具类
"""
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract


def main():
	result=pytesseract.image_to_string(Image.open('D:\\011111111111111111111111\\1545386170.6713.jpg'))
	print(result)


if __name__ =='__main__':
	train.train_crack_captcha_cnn()
	#main()