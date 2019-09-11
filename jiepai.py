# 分析jax
import requests
from lxml import etree
import json,re
from urllib.parse import urlencode
from requests.exceptions import RequestException
'''

def get_page_index(offset,keyword):
	data = {
		'aid':24,
		'en_qc':1,
		'offset':offset,
		'format':'json',
		'keyword':keyword,
		'autoload':'true',
		'count':'20',
		'cur_tab':1
	}
	url = 'https://www.toutiao.com/api/search/content/?' + urlencode(data)
	try:	
		response = requests.get(url)
		response.encoding = 'utf-8'
		if response.status_code == 200:
			return response.text
	except RequestException:
		print('请求索引出错')
		return None
def parse_page_index(html):
	data = json.loads(html)
	#print(data_list)

	if not len(data_list):
			print ("data_list长度为0")
			return
	for data in data_list:
		#yield data.get('article_url')
		print(data["article_url"])

	if data and 'data' in data.keys():
		#print(data.get('data'))
		#print(data.get('data')[18])
		
		for item in data.get('data'):
			#print("*"*40)
			if item.get('article_url'):
				yield item.get('article_url')
			#yield item.get('article_url')
def get_page_detail(url):
	try:
		response = requests.get(url)
		response.encoding = 'utf-8'
		if response.status_code == 200:
			print('1')
			print(response.text)
		else:
			print('连接错误')
			return None
	except RequestException:
		print('请求详情出错')
		return None
def parse_page_img(html):
	#soup = BeautifulSoup(html, 'html.parser')
	#title = soup.select('title')[0].get_text()
	html = etree.HTML(html)
	title = html.xpath('//title/text()')
	print(title)
	images_pattern = re.compile('JSON.parse(.*?),', re.S)
	result = re.search(images_pattern, html)
	if result:
		print(result.group(1))


def main():

	html = get_page_index(0,'街拍')
	#print(html)
	#data_list = json.loads(response.body)['data']
	#parse_page_index(html)
	for url in parse_page_index(html):
		if url:
			print(url)
			response = requests.get(url,verify=False)

			response.encoding = 'utf-8'
			print(response.text)
			#get_page_detail(url)
			#print('*'*40)
			#print(html)
		#if html:
			#parse_page_detail(html)


if __name__ == '__main__':
	#main()
'''
url = "https://www.toutiao.com/a6669576220562162179"
response = requests.get(url)
#response.encoding = 'utf-8'
html = etree.HTML(response.text)
title = html.xpath('//title/text()')[0]
print(title)

images_pattern = re.compile('JSON.parse\("(.*?)"\)',re.S)
result = re.search(images_pattern, response.text.encode)
print(result.group(1))

data = json.loads(result.group(1))
print(type(data))

if data and 'sub_images' in data.keys():
	sub_images = data.get('sub_images')
	images = [item.get('url') for item in sub_images]
	for image in images:
		print(image)
