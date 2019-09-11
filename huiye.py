import requests, json, os
import asyncio
import aiohttp
from lxml import etree

i_url = 'http://www.yhdm.tv/show/4355.html'
server = 'http://www.yhdm.tv'
root_path = 'F:\\pyData\\辉夜MP4'
headers = {
	'Referer': 'http://www.yhdm.tv/search/%E8%BE%89%E5%A4%9C/',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3676.400 QQBrowser/10.4.3505.400',
}
fail_urls = []

# 百度短网址
# url_short = 'https://dwz.cn/fIomEtD6'
# 将短网址转化为原网址
def change_url(url_short):
	base_url = 'https://dwz.cn/admin/v2/query'

	method = 'POST'
	content_type = 'application/json'

	# 设置Token
	token = '0b82e364e9abc6bc03a9761961c3dd25'

	# T设置待还原的短网址
	bodys = {'shortUrl':'%s' % url_short}

	# 配置headers
	headers = {'Content-Type':content_type, 'Token':token}

	# 发起请求
	response = requests.post(url=base_url, data=json.dumps(bodys), headers=headers)

	# 读取响应
	r = json.loads(response.text)

	if r['Code'] == 0:
		url_long = r['LongUrl']
		return url_long
	else:
		print('转化失败！')

# 获得所有章节url
def get_chapter(i_url):
	r = requests.get(i_url, headers = headers, verify = False)
	r.encoding = r.apparent_encoding
	s = etree.HTML(r.text)

	chapter_list = s.xpath('//div[@class="movurl"]//a/@href')

	for index, url in enumerate(chapter_list):
		yield index, server + url

# 将文件保存到本地
def file_store(r, chapter_path):
	with open(chapter_path, 'wb') as f:
		f.write(r.content)

# 从短链接中提取最终链接
def url_split(s):
	s = s.split('$')
	if s[1] != 'mp4':
		print('未找到视频url!')
	else:
		return s[0]

# 视频下载
def comic_download(html, chapter_path):
	s = etree.HTML(html)
	url = s.xpath('//div[@id="playbox"]/@data-vid')[0]
	url_short = url_split(url)
	url_long = change_url(url_short)
	r = requests.get(url_long)
	if not os.path.exists(chapter_path):
		file_store(r, chapter_path)
	else:
		print('%s已存在！' % chapter_path)

# 获取短链接
async def get_file(index, chapter_url):
	global fail_urls
	headers = {
		'Host': 'www.yhdm.tv',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3676.400 QQBrowser/10.4.3505.400',
	}
	try:
		async with aiohttp.ClientSession() as session:
			async with session.request('GET', chapter_url, headers = headers) as resp:
				html = await resp.text()
				title = '第%02d集.mp4' % index

				chapter_path = os.path.join(root_path, title)
				print('正在下载到：%s' % chapter_path)

				comic_download(html, chapter_path)
	except Exception as e:
		print(e)
		fail_urls.append(chapter_url)

# 调用方
def main():
	loop = asyncio.get_event_loop()
	tasks = [get_file(index, chapter_url) for index, chapter_url in get_chapter(i_url)]
	loop.run_until_complete(asyncio.wait(tasks))
	loop.close()

if __name__ == '__main__':
	main()
	if len(fail_urls) != 0:
		print('失败链接列表：')
		print(fail_urls)
	print('下载完成！')