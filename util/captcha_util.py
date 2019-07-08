# -*- coding: utf-8 -*-
"""
光学识别验证码工具类
"""
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
from collections import defaultdict








def get_black_photo(path:str):
	img = Image.open(path)
	Img = img.convert('L')
	threshold = 200
	table = []
	for i in range(256):
		if i < threshold:
			table.append(0)
		else:
			table.append(1)

	# 图片二值化
	photo = Img.point(table, '1')
	photo.save(path)
	return Image.open(path)

def main():
	# im=Image.open('D:\\011111111111111111111111\\9F028DBA2ACA23904E.gif')
	# im = im.convert('L')
	# im.save('D:\\011111111111111111111111\\222.png')

	text=pytesseract.image_to_string(get_black_photo('D:\\011111111111111111111111\\temp.png'),lang='chi_sim')
	# text=OCR_lmj('D:\\011111111111111111111111\\222.png')
	print(text)


if __name__ =='__main__':
	# train.train_crack_captcha_cnn()
	main()