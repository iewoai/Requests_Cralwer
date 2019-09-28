import requests
import re
import os
# import threading
import time
import pickle
# from proxypool_test import get_proxy
from lxml import etree
import base64


def base64Decode(s):
    bs = str(base64.b64decode(s), "utf-8")
    img_list = bs.split('$qingtiandy$')
    return img_list


def file_store(path, r):
    with open(path, 'wb') as f:
        f.write(r.content)
    print('下载成功！')


class mh67:
    def __init__(self, index, path):
        self.headers = {
            "USER-AGENT": 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3730.400 QQBrowser/10.5.3805.400'}
        self.index = index
        self.path = path
        self.url = ''
        self.title = ''
        self.failed_url = []
        self.server = 'http://m.67manhua.com'

    def img_download(self):
        r = requests.get(self.index, headers=self.headers)
        r.encoding = r.apparent_encoding
        s = etree.HTML(r.text)
        url_list = s.xpath('//div[@id="list"]//a/@href')
        title_list = s.xpath('//div[@id="list"]//a[@href]//span/text()')
        print(len(url_list))
        for i, url in enumerate(url_list):
            title = re.sub('[\/:*?"<>|]', '-', title_list[i])
            self.url =  self.server + url
            self.title = title
            self.get_img()
        print('失败链接如下：')
        print(self.failed_url)

    def get_img(self):
        chapter_path = os.path.join(self.path, self.title)
        if not os.path.exists(chapter_path):
            os.mkdir(chapter_path)
        c_r = requests.get(self.url, headers=self.headers)
        c_r.encoding = c_r.apparent_encoding
        s = re.findall(r'.*?qTcms_S_m_murl_e="(.*?)"', c_r.text, re.S)[0]

        # 头几章加载失败，img_list为a
        img_list = base64Decode(s)
        if not img_list[0] == 'a':
            for index, img in enumerate(img_list):
                img_path = os.path.join(chapter_path, '%03d.jpg' % index)
                print('图片链接为：%s' % img)
                if not os.path.exists(img_path):
                    print('正在下载到%s：' % (img_path))
                    try:
                        r = requests.get(img, headers=self.headers)
                        file_store(img_path, r)
                    except Exception as e:
                        print('下载失败！')
                        print('错误原因如下：')
                        print(e)
                        self.failed_url.append(img)
                else:
                    print('%s已存在！' % (img_path))
        else:
            print('图片地址错误!')

    '''
    # 原本想通过获取request_headers的location来换取图片地址的，后来在js中发现可以直接base解密变量qTcms_S_m_murl_e的值
    def get_request_location(self):
        test = 'http://img.686868g.com:899/statics/pic/?p=http%3A//mhpic.cnmanhua.com/comic/Dc1c12Fc1c1E6c1c196c1c197c1c1E7c1c1BDc1c197c1c1E5c1c1A4c1c1A7c1c1E9c1c199c1c1863c1c1E9c1c1BEc1c199c1c1E7c1c18Ec1c18Bc1c1E4c1c1BCc1c1A0c1c1E8c1c1AFc1c1B4c1c1E6c1c18Bc1c186c1c1E5c1c188c1c186c1c1E7c1c189c1c188c1c12Fc1c1E7c1c1ACc1c1AC6c1c1E8c1c1AFc1c19Dc1c12F6.jpg-mht.middle&wapif=1&picid=19163&m_httpurl='
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3732.400 QQBrowser/10.5.3819.400',
            'Referer': 'http://m.67manhua.com/67/19163/419236.html?p=5',
            'host': 'img.686868g.com:899',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }
        res = requests.post(url=test, headers=headers, allow_redirects=False) # 注 allow_redirects=False是必须的

        print(res.headers['location'])
    '''


if __name__ == '__main__':

    start = time.time()
    # 更改index可爬取67漫画网上其他漫画（如以下）
    # index = 'http://mip.67manhua.com/67/19163/'# 斗罗大陆3龙王传说
    # index = 'http://m.67manhua.com/67/772/'# 斗罗大陆外界传说
    # index = 'http://m.67manhua.com/67/11069/'# 斗破苍穹
    # index = 'http://m.67manhua.com/67/19162/'# 斗罗大陆
    index = 'http://m.67manhua.com/67/19204/'# 武动乾坤
    path = 'D:\\PyData\\wudongqiankui'
    mh = mh67(index, path)
    mh.img_download()
    print('总耗时：%.5f秒' % float(time.time()-start))
