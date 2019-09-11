# 下载一个网页上的小说文章内容（某一节）
# 下载一本小说所有章节文章内容
# 将所有章节的内容合并为完整的书
# 下载一个页面所有小说
# 下载n个页面所有小说
# 下载整个网站所有的小说
from bs4 import BeautifulSoup
import requests
import re,os,random
# import time,sys
headers = {}
headers['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36"
class book:	
	def  __init__(self,target,server):
	# 构造函数
		self.server = server
		self.target = target
		self.names = []
		self.urls = []
		self.nums = 0
		self.bname = ''
	def get_list_url(self):
	# 获取每一本书的目录url
		req = requests.get(self.target,headers = headers)
		html = req.text
		m_bf = BeautifulSoup(html,'html.parser')
		m = m_bf.find_all('div',class_='btnzone')
		n_bf = BeautifulSoup(str(m),'html.parser')
		n = n_bf.find_all('a')
		l = n[1].get('href')
		self.target = self.server+l

	def get_download_url(self):
	# 获取每一章节的url
		req = requests.get(self.target,headers = headers)
		html = req.text
		dd_bf = BeautifulSoup(html,'html.parser')
		# sm = dd_bf.find_all('div',id='info')
		string = dd_bf.title.string
		self.bname = re.split(r'\s',string)[0]
		# 获得每一本书的书名
		dd = dd_bf.find_all('dd',id='chapterlist')
		# print(str(dd))
		a_bf = BeautifulSoup(str(dd),'html.parser')
		a = a_bf.find_all('a')
		self.nums = len(a)
		for each in a:
			self.names.append(each.string)
			self.urls.append(self.server + each.get('href'))
			# print(link.string,self.server + link.get('href'))
			
	def get_contents(self, target):
	# 获得文本
		req = requests.get(url = target,headers = headers)
		html = req.text
		dd_bf = BeautifulSoup(html,'html.parser')
		dd = dd_bf.find_all('dd',id='contents')
		texts = dd[0].text
		return texts

	def writer(self,name,path,text):
	# 下载的内容写入文件
		write_flag = True
		with open(path,'a',encoding='utf-8') as f:
			f.write(name + '\n')
			f.writelines(text)
			f.write('\n\n')

def get_all_urls(url,ser):
	a = []
	req = requests.get(url,headers = headers)
	html = req.text
	m_bf = BeautifulSoup(html,'html.parser')
	m = m_bf.find_all('a',href=re.compile("/book/"))
	# print(len(m))
	b = len(m)
	for each in m[180:]:
		a.append(ser+each.get('href'))
	return a

if __name__ == '__main__':
	url = "https://www.bookbao99.net/Topten.html"
	ser = "https://www.bookbao99.net"
	a = get_all_urls(url,ser)
	for x in a:
		f = book(x,ser)
		f.get_list_url()
		f.get_download_url()
		bn = f.bname+'.txt'
		p = 'F://pyData//nb//'+bn
		try:
			if(f.nums>0):
				print('《'+f.bname+'》开始下载:')
				if not os.path.exists(p):
				# 判断文件是否存在
					for i in range(f.nums):
						f.writer(f.names[i],p,f.get_contents(f.urls[i]))
						# 控制台下进度条
						# sys.stdout.write("已下载:{0}{1}".format("|"*i,'%.3f%%' % float(i*100/f.nums) + '\r')
						# sys.stdout.flush()
						# time.sleep(0.5)
					print('《'+f.bname+'》下载完成！')
				else:
					print("文件已存在！")
			else:
				print('《'+f.bname+'》下载失败！')
		except:
			print("爬取失败！")

