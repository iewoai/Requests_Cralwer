import requests
import re
import os
import threading
import time
import pickle
from proxypool_test import get_proxy
from lxml import etree

# index_url = 'https://www.mh1234.com/wap/comic/10098.html'
index_url = 'http://www.mh1234.com/wap/comic/10869.html'
host = 'https://www.mh1234.com'
img_host = 'https://mhpic.dongzaojiage.com/'
# path = 'D:\\PyData\\douluo3'
path = 'D:\\PyData\\kuihuabaodian'

headers = {
    'Host': 'www.mh1234.com',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3730.400 QQBrowser/10.5.3805.400'

}


def file_store(path, r):
    with open(path, 'wb') as f:
        f.write(r.content)
    print('下载成功！')

def check_request(url, headers, **kw):
    try:
        if kw['proxy'] == '':
            r = requests.get(url, headers=headers)
        else:
            r = requests.get(url, headers=headers, proxies = kw['proxy'])
        return r
    except:
        ipprot = get_proxy()
        proxies = { "http": "http://"+str(ipprot) }
        print('正在切换ip：%s' % ipprot)
        kw= {'proxy' : proxies}
        check_request(url, headers, **kw)


def get_chapter(url):
    kw = {'proxy':''}
    check_request(url, headers, **kw)
    # r = requests.get(url, headers=headers)
    r.encoding = r.apparent_encoding
    s = etree.HTML(r.text)
    chapters = s.xpath('//ul[@id="chapter-list-1"]//a/@href')
    titles = s.xpath('//ul[@id="chapter-list-1"]//span/text()')
    print(0)
    for i in range(len(chapters)):
        chapter = host + chapters[i]
        title = re.sub('[\/:*?"<>|]', '-', titles[i])
        yield chapter, title
        # print(chapter, title)


def get_info(chapter, title):
    kw = {'proxy':''}
    check_request(chapter, headers, **kw)
    # r = requests.get(chapter, headers=headers)
    r.encoding = r.apparent_encoding
    print(r.text)
    img_info = re.findall(r'var chapterImages = \[(.*?)\];.*?var chapterPath = \"(.*?)\";.*?', r.text, re.S)[0]
    if img_info[1] == '':
        # img_list = ['https://mhpic.dongzaojiage.com' + i.replace('\\\\', '') for i in re.findall(r'\"(.*?)\"', img_info[0])]
        img_list = []
        for i in re.findall(r'\"(.*?)\"', img_info[0]):
            i = 'https://mhpic.dongzaojiage.com' + i.replace('\\', '')
            img_list.append(i)

    else:
        img_list = [img_host + img_info[1] + i for i in re.findall(r'\"(.*?)\"', img_info[0])]
    
    chapter_path = os.path.join(path, title)
    if not os.path.exists(chapter_path):
        os.mkdir(chapter_path)

    for index, img in enumerate(img_list):
        # print(img_list)
        img_path = os.path.join(chapter_path, '%04d.jpg' % index)
        img_headers = {
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3730.400 QQBrowser/10.5.3805.400'
        }

        print('正在下载到%s：' % (img_path))
        if not os.path.exists(img_path):
            kw = {'proxy':''}
            check_request(img, img_headers, **kw)
            # r = requests.get(img, headers = img_headers)
            file_store(img_path, r)
        else:
            print('%s已存在！' % (img_path))

def main():
    
    for chapter, title in get_chapter(index_url):
        get_info(chapter, title)
    
    # get_info('https://www.mh1234.com/wap/comic/10869/434651.html', '测试')

if __name__ == '__main__':
    start = time.time()
    main()
    print('总耗时：%.5f秒' % float(time.time()-start))

