import requests, re
from urllib.parse import urlencode
import pymysql
import redis,json
REDIS_HOST = "127.0.0.1"
REDIS_DB = 1
REDIS_PASSWORD = "a12345"
REDIS_PORT = 6379
redis_config = {
	"host":REDIS_HOST,
	"db":REDIS_DB,
	"port":REDIS_PORT,
	"charset":"utf-8",
	"password":REDIS_PASSWORD
}
'''
Accept-Language:zh-CN,zh;q=0.9
Connection:keep-alive
Cookie:_ntes_nnid=100a3fa84c4b4fd5767982dd72b99005,1547191029306; _ntes_nuid=100a3fa84c4b4fd5767982dd72b99005; __utma=94650624.1362362991.1547191030.1547191030.1547191030.1; __utmz=94650624.1547191030.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; WM_TID=dVoOajXBobFEQQAVFBItxArLsXPSzJTc; __oc_uuid=f7212aa0-248f-11e9-93df-c58482c7c1ee; _iuqxldmzr_=32; JSESSIONID-WYYY=mV%2F9%5CMtlEg%2FBC5wr01VaFWYnh00O4jY4u6vRcJlyGbrTw%5Czo4%5CQv8cec0y62GRzV2V5aNdtldbdQUkfxmDDIMdS6Ms3iffh5vh8IHqDDNyHdItCagIZ0Tt5gXMaidS%2BqIR8JSvoP3SaAJntulhe%5CBpWcX4moWb%5C5W0WvMRssHPbwas1%2F%3A1553221228015; WM_NI=P50XVKT1jAzNnH6w9Y%2Bj9J6Av1lpH3biVZZSU%2FsB62C5BNDfCtVVp4MSwcswjPKolFQ4Y%2F78%2FO4I27ml04YfF1dRWWruLDZom%2Fyo%2FC2sMukiz4rZLJmz0f1iwX9n4rmVOVM%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eeabe16ab3ad97afee4388eb8eb7c15b939f8aaabc74b1a981b6ee5490e8f8b7cf2af0fea7c3b92a94eb00b9d54198efa6a2f946ae98fa98bc53e9b6f7abb54bb6efa491cb39a2b79abbd95997f1bda3b53a81eb8eafc76e81ac9ab7f3408f8db984f27daa908590ef4e93ec97d0b634ed91fcaab13dafb400d5dc6e86efacb3d65db2ab84a5d965aff1b790ae49f2ad8396ea63baecbebbcf42afa60087b463b588f78fb77aaf8a81b7d037e2a3

User-Agent:Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.6824.400 QQBrowser/10.3.3137.400
'''

def get_connection(url):
	headers = {"USER-AGENT":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.6824.400 QQBrowser/10.3.3137.400"}
	response = requests.get(url,headers = headers)
	return response.text
#print(response.text)
def get_imformation(response):
	pattern = re.compile('<li.*?u-cover.*?src="(.*?)".*?class="nb">(.*?)</span>.*?title="(.*?)"\shref="(.*?)".*?title="(.*?)"\shref="(.*?)".*?</li>',re.S)
	results = re.findall(pattern, response)
	db = db_connection()
	cur = db.cursor()
	#print(results)
	for result in results:
		img_url,count,title,msc_list_url,user_name,user_url = result
		# http://p2.music.126.net/lnF1w6aESCJMM-p1MWmVWQ==/109951163678101279.jpg?param=140y140
		img_url = re.sub('140y140$','400y400',img_url)
		count = count.replace('万','0000')
		title = re.sub(r'[\\/:*?<>|\']', '_',title)
		msc_list_url = server + msc_list_url
		user_url = server + user_url
		key_id = re.search('(\d+)', msc_list_url)
		#print(img_url,count,title,msc_list_url,user_name,user_url)
		sql = 'insert into msc_list values(\'%s\', %s, \'%s\', \'%s\', \'%s\', \'%s\')' %(img_url,count,title,msc_list_url,user_name,user_url)
		try:
			cur.execute(sql)
		except pymysql.err.ProgrammingError:
			print(sql)
			continue
		#print(sql)
	db.close()
def get_redisconn():
	try:
		r = redis.StrictRedis(**redis_config)
		return r
		#当不传参数的时候，默认连接本地的6379端口，db为0
		print("redis连接成功%s"%r)
	except:
		print("redis连接异常")

def get_imformation_redis(response):
	pattern = re.compile('<li.*?u-cover.*?src="(.*?)".*?class="nb">(.*?)</span>.*?title="(.*?)"\shref="(.*?)".*?title="(.*?)"\shref="(.*?)".*?</li>',re.S)
	results = re.findall(pattern, response)
	#print(results)
	r= get_redisconn()
	for result in results:
		img_url,count,title,msc_list_url,user_name,user_url = result
		# http://p2.music.126.net/lnF1w6aESCJMM-p1MWmVWQ==/109951163678101279.jpg?param=140y140
		img_url = re.sub('140y140$','400y400',img_url)
		count = count.replace('万','0000')
		title = re.sub(r'[\\/:*?<>|\']', '_',title)
		msc_list_url = server + msc_list_url
		user_url = server + user_url
		key = re.search('(\d+)$', msc_list_url)
		list_id = key.group(1)
		data = {
			'img_url' : img_url,
			'count' : count,
			'title' : title,
			'msc_list_url' : msc_list_url,
			'user_name' : user_name,
			'user_url' : user_url
		}
		r.hset('163msc_list', list_id, json.dumps(data))
		#print(img_url,count,title,msc_list_url,user_name,user_url)
		#print(key_id)


def db_connection():
	db= pymysql.connect(host="localhost",user="root",
	password="123456",db="163msc_list",port=3306)
	return db

def get_page_index(offset):
	data = {
		'order':'hot',
		'cat':'全部',
		'limit':35,
		'offset':offset# 以35为间隔自增长
	}
	url = "https://music.163.com/discover/playlist/?"
	url = url + urlencode(data)
	return url
'''
if __name__ == '__main__':
	server = "https://music.163.com"
	offset = 0
	for i in range(1,38):
		url = get_page_index(offset)
		print(url)
		response = get_connection(url)
		get_imformation(response)
		offset += 35
		nexturl = get_page_index(offset)
	print("全部插入完成")
'''
if __name__ == '__main__':
	server = "https://music.163.com"
	offset = 0
	for i in range(1,38):
		url = get_page_index(offset)
		print(url)
		response = get_connection(url)
		get_imformation_redis(response)
		offset += 35
		nexturl = get_page_index(offset)
	print("全部插入完成")
