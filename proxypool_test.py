import sys
sys.path.append('D:\\PyStudy\\ProxyPool')
from proxypool.db import RedisClient

def get_proxy():
    g = RedisClient()
    return g.random()
