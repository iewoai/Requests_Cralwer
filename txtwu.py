from bs4 import BeautifulSoup
import requests, sys
import re,os,random
from lxml import etree
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
user_agent_list = [
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60",
	"Opera/8.0 (Windows NT 5.1; U; en)",
	"Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50",
	"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
	"Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
	"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
	"Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
	"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
	"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
	"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
	"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
	"Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0",
	"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.3.4000 Chrome/30.0.1599.101 Safari/537.36"
]
# 随机选取可用ip
'''
file = open("valid_ip_xicidaili.txt","r")
proxies_list = []
for line in file:
	proxies_list.append(line.strip().replace("\n",""))
proxy = {"https":random.choice(proxies_list)}
'''
# 利用一直获取下一页链接得到全书内容
# 获取每一本书的开始阅读
class wu:
	def __init__(self, target, server):
		self.target = target
		self.server = server
		self.path = ''
		self.name = ''
		self.txt = ''
# 建立连接，并转化为etree
	def get_etree(self,target):
		headers = {"USER-AGENT":random.choice(user_agent_list)}
		r= requests.get(target,headers = headers,verify=False)
		r.encoding = r.apparent_encoding
		html = etree.HTML(r.text)
		return html
# 获得阅读链接
	def get_read(self):
		html = self.get_etree(self.target)
		read = html.xpath('//span[@class="margin_right"]/a/@href')
		return server+"".join(read)
# 获取书名
	def get_name(self):
		html = self.get_etree(self.target)
		n = html.xpath('/html/head/meta[@property="og:novel:book_name"]/@content')#/html/head/meta[11]
		self.name = "".join(n).replace('/','')
# 获得每一个链接的文本
	def get_all_txt(self,target):
		html = self.get_etree(target)
		txt1 = html.xpath('//*[@id="nr1"]/text()')
		self.txt = "\n".join(txt1)
# 获得阅读中下一页链接,将下一页链接传到数组里(递归)
	def get_next_url(self, target):
		html = self.get_etree(target)
		# 目录url
		m_url = server+"".join(html.xpath('//*[@id="pt_next"]/@href'))
		# 下一页url
		n_url = server+"".join(html.xpath('//*[@id="pb_next"]/@href'))
		if (m_url == n_url):
			#for x in a:
			#	print(x)
			print("全部章节下载完成")
		else:
			#a.append(n_url)
			self.get_all_txt(n_url)
			self.writer()
			self.get_next_url(n_url)

	def writer(self):
		# 下载的内容写入文件
			write_flag = True
			with open(self.path,'a',encoding='utf-8') as f:
				f.writelines(self.txt)
	def txtwu(self):
		html = self.get_etree(self.target)
		# 下载一本书
		self.get_name()
		bname = self.name+'.txt'
		self.path = 'F://pyData//nb//'+bname
		url = self.get_read()
		#try:
		print('《'+self.name+'》开始下载:')
		print('《'+self.name+"》的储存地址为："+self.path)
		if not os.path.exists(self.path):
			self.get_next_url(url)

		else:
			print("文件已存在！")
		#except:
			#print("爬取失败！")

# txt = get_all_txt(url)
#a = []

# url = "https://m.txtwu.org/wapbook/3_3549_383545.html"
# 获得一页所有链接，再进行下载


def get_all_urls(url):
	r = requests.get(url)
	r.encoding = r.apparent_encoding
	html = etree.HTML(r.text)
	all = html.xpath('//a[contains(@href,"/wapbook/")]/@href')
	for x in all:
		print("正在开始下载第"+str(all.index(x)+1)+"本书")
		w = wu(server+x,server)
		w.txtwu()
		print("第"+str(all.index(x)+1)+"本下载完成")
server = "https://m.txtwu.org"
for n in range(3,11):
	url = "https://m.txtwu.org/top/allvisit_"+str(n)+"/"
	get_all_urls(url)

