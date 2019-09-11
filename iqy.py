import requests, json, re, os, time
from tqdm import tqdm
from subprocess import Popen

headers = {
	'Host': 'cache.m.iqiyi.com',
	'Connection': 'keep-alive',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36',
}

url = 'http://cache.m.iqiyi.com/mus/1032950400/3a86bf54faf6d33876b581e35897ad55/afbe8fd3d73448c9//20190507/5f/4b/c7d3b47d28c0da272aff877158a23d96.m3u8?qd_originate=tmts_py&tvid=1032950400&bossStatus=0&qd_vip=0&px=&src=3_31_312&prv=&previewType=&previewTime=&from=&qd_time=1561529421551&qd_p=3cb02825&qd_asc=481eac71f0d0027a46c3f6b831186e15&qypid=1032950400_04022000001000000000_4&qd_k=c7b2e2a14fb44c664cefb173c0a38dc8&isdol=0&code=2&ff=f4v&iswb=0&qd_s=otv&vf=84d358de121ea7778e8f832e2fcbad25&np_tag=nginx_part_tag'
mp4_name = '烟花.mp4'

audio_name = '烟花-灯塔.mp3'
audio_time = [['00:57:25', '00:03:41'], ['01:08:10', '00:01:06']]
path = 'F:\\pyData\\you_get\\iqy'
concat_path = os.path.join(path, 'filelist.txt')
mp4_path = 'F:\\pyData\\you_get\\%s' % mp4_name
audio_path = 'F:\\pyData\\you_get\\%s' % audio_name

def ff_com():
	if not os.path.exists(mp4_path):
		pp = Popen(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', concat_path, '-c', 'copy', '-bsf:a', 'aac_adtstoasc', mp4_path])
		t0 = time.time()
		while time.time()-t0 < 60:
			ret = pp.poll()
			if not (ret is None):
				break
			time.sleep(1)
		ret = pp.poll()
		if ret is None:
			print('合成失败，强行终止')
			pp.terminate()
		else:
			print('合成成功，所需时间： %ds' % (time.time()-t0))
	else:
		print('%s已存在' % mp4_path)

def iqy_download(url):
	r = requests.get(url = url, headers = headers)

	urls = re.findall(r',(.*?)#', r.text, re.S)
	concat = []

	if len(urls) != 0:
		print('开始下载%s：' % mp4_name)
		
		for i,url in tqdm(enumerate(urls)):
			url = re.sub(r'\s|\n', '', url)
			file_path = '%d.ts' % i
			file_path = os.path.join(path, file_path)

			concat.append('file \'%s\'\n' % file_path)

			r = requests.get(url)
			with open(file_path, 'wb') as f:
				f.write(r.content)
		with open(concat_path, 'w') as f:
			f.writelines(concat)

		ff_com()

def delete_tempFile(path):
	if os.path.exists(mp4_path):
		print('正在删除临时文件：')
		t0 = time.time()
		file_list = os.listdir(path)
		for file in tqdm(file_list):
			file_path = os.path.join(path, file)
			os.remove(file_path)
		print('删除临时文件完成，所需时间：%d' % (time.time() - t0))

def audio_cut():
	if not os.path.exists(audio_path):
		print('正在生成%s：' % audio_name)
		concat = []
		for i, audio in enumerate(audio_time):
			temp_path = 'F:\\pyData\\you_get\\%d.mp3' % i
			concat.append('file \'%s\'\n' % temp_path)

			if not os.path.exists(temp_path):
				pp = Popen(['ffmpeg', '-i', mp4_path, '-ss', audio[0], '-t', audio[1], '-f', 'mp3', '-vn', temp_path])
				t0 = time.time()
				while time.time()-t0 < 100:
					ret = pp.poll()
					if not (ret is None):
						break
					time.sleep(1)
				ret = pp.poll()
				if ret is None:
					print('裁剪失败，强行终止')
					pp.terminate()
				else:
					print('裁剪成功，所需时间： %ds' % (time.time()-t0))

		with open(concat_path, 'w') as f:
			f.writelines(concat)
		print('正在合成临时文件：')

		pp = Popen(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', concat_path, '-c', 'copy', audio_path])
		t0 = time.time()
		while time.time()-t0 < 100:
			ret = pp.poll()
			if not (ret is None):
				break
			time.sleep(1)
		ret = pp.poll()
		if ret is None:
			print('合成失败，强行终止')
			pp.terminate()
		else:
			print('合成成功，所需时间： %ds' % (time.time()-t0))
		print('生成成功')



if __name__ == '__main__':
	# iqy_download(url)
	# delete_tempFile(path)
	# audio_cut()