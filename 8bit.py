import requests, re, json, pickle, os
from urllib.parse import urlencode
class bit:
    def __init__(self):
        self.headers = {"USER-AGENT":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.6824.400 QQBrowser/10.3.3137.400"}
        self.start_url = 'https://webapi.8btc.com/bbt_api/news/list?'
        self.path = '8bit.p'
        self.data = {}
        self.data_new = {}

        self.hot_sum = 0
        self.item_num = 0

    # 获取每篇文章部分详情
    def get_more(self, url):
        html = requests.get(url, headers = self.headers).text
        # html = response.encode('GBK','ignore').decode('GBk')
        s = re.findall(r'<div class="bbt-html".*?>(.*?)</div>', html, re.S)[0]
        #将匹配到的内容用空替换，即去除匹配的内容，只留下文本
        text = re.sub(r'\s|\n|<[^>]+>', '', s)
        info = text[:75]
        images_num = len(re.findall(r'src="(.*?)"', s, re.S))
        likes = re.findall(r'<button class="bbt-btn bbt-btn--primary share-module__item".*?<i class="bbt-icon bbt-icon-thumb-up".*?</i>.*?(\d+).*?</button>', html, re.S)[0]
        likes = int(likes)
        collections = 0
        comments = re.findall(r'<a.*?class="link-dark-minor share-module__item".*?</i>.*?(\d+).*?</a>', html, re.S)[0]
        comments = int(comments)
        return comments,text,likes,collections,images_num,info

    # 本地读取data数据
    def set_data(self):
        if os.path.exists(self.path):
            tem = pickle.load(open(self.path, 'rb'))
            self.data = tem

    def get_data(self):
        self.get_8bit()
        for i in self.data:
            yield self.data[i]

    # 最新文章生成器
    def get_newst_data(self):
        self.get_8bit()
        for i in self.data_new:
            yield self.data_new[i]

    def get_8bit(self):
        self.set_data()
        page = 1
        num = 0
        print('爬取开始：')
        while True:
            offset = {
                    'post_type':'post',
                    'num':20,
                    'page':page,
                    'tag_slug':'bytom'
                }

            start_url = self.start_url + urlencode(offset)

            response = requests.get(start_url, headers = self.headers).text

            result = json.loads(response)
            
            if result['code'] == 200 and len(result['data']['list']) != 0:
                for art in result['data']['list']:
                    bit_id = '8bit_%d' % art['id']

                    if not (bit_id in self.data):
                        num += 1
                        url = 'https://www.8btc.com/article/%d' % art['id']

                        title = art['title']

                        time = int(art['post_date'])

                        views = int(art['views'])

                        author_name = art['author_info']['display_name']
                        try:
                            avatar_url = art['author_info']['avatars'][-1]
                        except:
                            # print(art['author_info']['avatars'])
                            avatar_url = 0

                        a = []
                        for tag_name in art['tags']:
                            a.append(tag_name['name'])
                        tag = ','.join(a)

                        comments,text,likes,collections,images_num,info = self.get_more(url)

                        hot = views*1+comments*2+images_num*0.7+likes*1.5

                        self.data[bit_id] = {
                                        'url' : url,
                                        'title' : title,
                                        'time' : time,
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
                        self.data_new[bit_id] = self.data[bit_id]
                page += 1
            elif len(result['data']['list']) == 0:
                print('爬取结束，没有更多结果')
                break
            elif result['code'] != 200:
                print('请求错误')
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
    bit = bit()
    data_all = bit.get_data()

    print('正在提取全部文章：')
    for data in data_all:
        print(str(data).encode('GBK','ignore').decode('GBk'))

    data_new = bit.get_newst_data()

    print('正在提取最新文章：')
    for data in data_new:
        print(str(data).encode('GBK','ignore').decode('GBk'))
