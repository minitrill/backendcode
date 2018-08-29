#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/25 10:43
# @Author  : 曾凌峰
# @Site    : 
# @File    : cachecontroller.py
# @Software: PyCharm

from models import static
from models import RedisClient
from config import config, static
from utils import validhash

initial_expire = 10
add_expire = 2
split_symbol = '&'

class CacheKey:
    @staticmethod
    def video_key(vid):
        return config.VIDEO_TABLE_BASE_NAME+split_symbol+str(vid)

    @staticmethod
    def user_key(uid):
        return config.USER_TABLE_BASE_NAME+'_'+str(static.get_table_num(uid))+split_symbol+str(uid)

    @staticmethod
    def comment_key(cid):
        return config.VIDEO_COMMENT_TABLE_BASE_NAME+split_symbol+str(cid)


class Cache(object):
    """
    Read/Write Through Pattern && Cache Aside Pattern
    缓存策略：
    meta层，记录data层key值的有效时间
    data层，记录具体缓存数据

    data层命中，则对expire time新增5s

    meta层无法命中而data层命中，将数据回写mysql，并清除data层记录（由过期事件订阅完成）

    meta层data层都无法命中，则从mysql读取数据，并更新至meta和data层。初始数据expire time 20s
    """
    def __init__(self, config):
        # if not isinstance(client, RedisClient):
        #     raise TypeError('Cache client should be RedisClient type')
        #self.client = client
        self.client = RedisClient(config)

    @property
    def meta(self):
        return self.client.meta

    @property
    def data(self):
        return self.client.data

    def getvideo(self, vid):
        key = CacheKey.video_key(vid)
        if not self.data.exists(key):
            return None
        video = self.data.hgetall(key)
        if video and self.meta.exists(key):
            ttl = self.meta.ttl(key)
            #用set取代expire是为了避免expire错误。meta的key值用于记录时间信息，value值不重要
            self.meta.set(key, key, ex=ttl+add_expire) if ttl else self.meta.set(key, key, ex=initial_expire)
        return video

    def setvideo(self, videoid, **video):
        key = CacheKey.video_key(videoid)
        # 缓存干净，插入数据
        self.data.hmset(key, video)
        self.meta.set(key, key, ex=initial_expire)
        return True
        # if not(self.data.exists(key) or self.meta.exists(key)):
        # else:

    def likevideo(self, vid):
        key = CacheKey.video_key(vid)
        if not self.data.exists(key):
            return False
        self.data.hincrby(key, 'like', 1)
        ttl = self.meta.ttl(key)
        # 用set取代expire是为了避免expire错误。meta的key值用于记录时间信息，value值不重要
        self.meta.set(key, key, ex=ttl + add_expire) if ttl else self.meta.set(key, key, ex=initial_expire)
        return True

    def sharevideo(self, vid):
        key = CacheKey.video_key(vid)
        if not self.data.exists(key):
            return False
        self.data.hincrby(key, 'share', 1)
        ttl = self.meta.ttl(key)
        # 用set取代expire是为了避免expire错误。meta的key值用于记录时间信息，value值不重要
        self.meta.set(key, key, ex=ttl + add_expire) if ttl else self.meta.set(key, key, ex=initial_expire)
        return True

    def viewvideo(self, vid):
        key = CacheKey.video_key(vid)
        if not self.data.exists(key):
            return False
        self.data.hincrby(key, 'view', 1)
        ttl = self.meta.ttl(key)
        # 用set取代expire是为了避免expire错误。meta的key值用于记录时间信息，value值不重要
        self.meta.set(key, key, ex=ttl + add_expire) if ttl else self.meta.set(key, key, ex=initial_expire)
        return True

    def getuser(self, uid):
        key = CacheKey.user_key(uid)
        if not self.data.exists(key):
            return None
        user = self.data.hgetall(key)
        if user and self.meta.exists(key):
            ttl = self.meta.ttl(key)
            # 用set取代expire是为了避免expire错误。meta的key值用于记录时间信息，value值不重要
            self.meta.set(key, key, ex=ttl + add_expire) if ttl else self.meta.set(key, key, ex=initial_expire)
        return user

    def setuser(self, userid, **user):
        key = CacheKey.user_key(userid)
        # 缓存干净，插入数据
        self.data.hmset(key, user)
        self.meta.set(key, key, ex=initial_expire)
        return True

    def deleteuser(self, uid):
        key = CacheKey.user_key(uid)
        self.meta.delete(key)
        self.data.delete(key)

    def deletevideo(self, vid):
        key = CacheKey.video_key(vid)
        self.meta.delete(key)
        self.data.delete(key)


if __name__ == '__main__':
    import pymysql
    conn = pymysql.Connection(
        host='118.126.104.182',
        port=3306,
        db='minitrill',
        user='root',
        password='19950705',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    vid="6460702604455316749"
    cursor.execute('SELECT * FROM Video WHERE vid = \"{vid}\"'.format(vid=vid))
    result = cursor.fetchone()
    client = RedisClient(config)
    key = CacheKey.video_key(vid)
    client.data.hmset(key, result)
    rs=client.data.hgetall(key)
    from models import SQL_refector
    sql = SQL_refector.video_update(vid, **rs)
    print sql