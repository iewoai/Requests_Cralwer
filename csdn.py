import requests, re, json, pickle, os
from urllib.parse import urlencode
from lxml import etree
import time

class csdn:
	def __init__(self):
		self.headers = {"USER-AGENT":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.6824.400 QQBrowser/10.3.3137.400"}
		self.start_url = 'https://so.csdn.net/so/search/s.do?'
		self.path = 'csdn.p'
		self.data = {}
		self.data_new = {}

	def set_data(self):
		if os.path.exists(self.path):
			tem = pickle.load(open(self.path, 'rb'))
			self.data = tem

	def get_data(self):
		self.get_csdn()
		for i in self.data:
			yield self.data[i]

	def get_newst_data(self):
		self.get_csdn()
		for i in self.data_new:
			yield self.data_new[i]

	def get_more(self, url):
		html = requests.get(url, headers = self.headers).text
		s = etree.HTML(html)
		title = s.xpath('//h1[@class="title-article"]/text()')[0]
		
		c_time = s.xpath('//span[@class="time"]/text()')[0]
		timeArray = time.strptime(c_time, "%Y年%m月%d日 %H:%M:%S")
		c_time = int(time.mktime(timeArray))

		views = s.xpath('//span[@class="read-count"]/text()')[0]
		views = re.findall(r'\d+', views)[0]
		
		comments = s.xpath('//span[@class="hover-show text"]/following-sibling::p/text()')[0].strip()
		if comments == '':
			comments = 0
		
		likes = s.xpath('//span[@class="hover-show text-box text"]/following-sibling::p/text()')[0].strip()
		
		collections = 0

		author_name = s.xpath('//a[@id="uid"]/text()')[0]

		avatar_url = s.xpath('//img[@class="avatar_pic"]/@src')[0]

		images_num = s.xpath('//div[@id="content_views"]//img')

		tag = 0
		# xpath外加string时会提取标签内所有文字，但是会保留空格和换行
		text = s.xpath('string(//div[@id="content_views"])')
		# 去空格和换行
		text = re.sub(r'\s|\n', '', text)
		# 缩略文字
		info = text[:75]
		return title,c_time,int(views),int(comments),int(likes),collections,author_name,avatar_url,len(images_num),tag,text,info

	def get_csdn(self):
		page = 1
		num = 0
		self.set_data()
		print('爬取开始：')
		while True:
			offset = {
				'p' : page,
				'q' : 'bytom'
			}
			start_url = self.start_url + urlencode(offset)
			r = requests.get(start_url, headers = self.headers)
			r.encoding = r.apparent_encoding
			html = r.text
			urls = re.findall(r'"con":"(https://blog\.csdn\.net/.*?/article/details.*?)"}', html, re.S)
			if len(urls) != 0:
				for url in set(urls):
					csdn_id = 'csdn_%s' % url.split('/')[-1]
					if not (csdn_id in self.data):
						num += 1
						title,c_time,views,comments,likes,collections,author_name,avatar_url,images_num,tag,text,info = self.get_more(url)
						
						hot = views*1+comments*2+images_num*0.7+likes*1.5

						self.data[csdn_id] = {
												'url' : url,
												'title' : title,
												'time' : c_time,
												'views' : views,
												'comments' : comments,
												'likes' : likes,
												'collections' : collections,
												'author_name' : author_name,
												'avatar_url' : avatar_url,
												'images_num' : images_num,
												'tag' : tag,
												'text' : text,
												'info' : info,
												'hot' : hot,
												}
						self.data_new[csdn_id] = self.data[csdn_id]
				page += 1
			else:
				print('爬取结束，没有更多结果')
				break

		if num > 0:
			try:
				with open(self.path, 'wb') as f:
					print('开始储存')
					pickle.dump(self.data, f)
					f.close()
			except:
				print('储存失败')
			finally:
				print('储存完毕')

		print('本次共爬取了%d个结果。' % num)



if __name__ == '__main__':
	cn = csdn()

	data_all = cn.get_data()

	print('正在提取全部文章：')
	for data in data_all:
		print(str(data).encode('GBK','ignore').decode('GBk'))

	data_new = cn.get_newst_data()

	print('正在提取最新文章：')
	for data in data_new:
		print(str(data).encode('GBK','ignore').decode('GBk'))
