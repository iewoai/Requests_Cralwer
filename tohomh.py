import requests
import re
import os
import threading
import time
import pickle
from lxml import etree

headers = {
    'Host': 'www.tohomh123.com',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3730.400 QQBrowser/10.5.3805.400'

}
index_url = 'https://www.tohomh123.com/doupocangqiongmanhua/'
host = 'https://www.tohomh123.com/'
threadNum = 8
path = 'D:\\PyData\\doupo'


def get_chapter(index_url):
    html = requests.get(index_url, headers=headers).text
    s = etree.HTML(html)
    chapters = s.xpath('//ul[@id="detail-list-select-1"]//a/@href')

    titles = s.xpath('//ul[@id="detail-list-select-1"]//a/text()')

    for i in range(len(chapters)):
        chapter = host + chapters[i]
        title = re.sub('[\/:*?"<>|]', '-', titles[i])
        yield chapter, title


def get_info(chapter, title):
    html = requests.get(chapter, headers=headers).text

    info = re.findall(
        r".*?var did=(.*?);.*?var sid=(.*?);.*?var pcount = (.*?);.*?var pl = '(.*?)';.*?", html, re.S)[0]

    did, sid, pcount, p1 = info[0], info[1], info[2], info[3]
    chapter_path = os.path.join(path, title)
    if not os.path.exists(chapter_path):
        os.mkdir(chapter_path)

    p1_path = os.path.join(chapter_path, '0000.jpg')
    yield p1_path, p1
    for i in range(2, int(pcount)+1):
        img_php = 'https://www.tohomh123.com/action/play/read?did=%s&sid=%s&iid=%d' % (
            did, sid, i)
        img_path = os.path.join(chapter_path, '%04d.jpg' % i)

        html = requests.get(img_php, headers=headers).text
        img_url = re.findall(r'"Code":"(.*?)"', html)[0]
        yield img_path, img_url

# 储存图片


def file_store(path, r):
    with open(path, 'wb') as f:
        f.write(r.content)
    print('下载成功！')


class threadDownload(threading.Thread):
    def __init__(self, que):
        threading.Thread.__init__(self)
        self.que = que

    def run(self):

        for i in self.que:
            host = re.findall(r'//(.*?)/', i[1])[0]
            print(host)
            headers = {
                'Host': host,
                'Connection': 'keep-alive',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3730.400 QQBrowser/10.5.3805.400'
            }

            r = requests.get(i[1], headers=headers)
            print('正在下载到%s：' % (i[0]))
            if not os.path.exists(i[0]):
                file_store(i[0], r)
            else:
                print('%s已存在！' % (i[0]))


def main():
    print('正在爬取所有图片链接！')
    img_info = []
    for chapter, title in get_chapter(index_url):
        for img_path, img_url in get_info(chapter, title):

            img_info.append([img_path, img_url])
    print('所有图片链接爬取完成！')
    with open('doupo_info.p', 'wb') as f:
        print('开始储存————————')
        pickle.dump(img_info, f)
        f.close()
    print('储存成功————————')
    length = len(img_info)
    queList = []

    for i in range(threadNum):
        que = []
        left = i * (length // threadNum)
        if (i+1) * (length // threadNum) < length:
            right = (i+1) * (length // threadNum)
        else:
            right = length
        for url in img_info[left:right]:
            que.append(url)
        queList.append(que)
    threadList = []
    print(queList)
    for i in range(threadNum):
        threadList.append(threadDownload(queList[i]))
    for thread in threadList:
        thread.start()
    for thread in threadList:
        thread.join()


if __name__ == '__main__':
    start = time.time()
    main()
    print('总耗时：%.5f秒' % float(time.time()-start))
