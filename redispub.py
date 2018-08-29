#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/17 16:36
# @Author  : 曾凌峰
# @Site    : 
# @File    : redispub.py
# @Software: PyCharm

"""
该模块是订阅redis中的key过期事件，当meta层中的key过期后，将data层将数据回写mysql
TODO 考虑redis异常的情况，数据持久化
"""
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from config import config
from models import SQL_refector, RedisClient

import redis
import pymysql
import utils
import os
import traceback

split_symbol = '&'

#将订阅和发送集合到一个类中了
class RedisPub:
    def __init__(self):
        self._db = pymysql.Connection(
            host = config.TORMYSQL_HOST,
            port = config.TORMYSQL_PORT,
            user=config.TORMYSQL_USER,
            passwd=config.TORMYSQL_PASSWORD,
            charset='utf8mb4',
            db=config.TORMYSQL_DB,
            use_unicode=False,
        )
        self._logger = utils.get_logger(
            debug=True,
            loggername='redispub',
            file=os.path.join(config.LOG_PATH, 'redispub.log')
        )
        self._cursor = self._db.cursor()
        self._redis = RedisClient(config)
        self.chan_sub = "__keyevent@6__:expired"#接收的波段
        self.chan_pub = "__keyevent@6__:expired"#发送的波段

    @property
    def meta(self):
        return self._redis.meta

    @property
    def data(self):
        return self._redis.data

    @property
    def cursor(self):
        return self._cursor

    @property
    def logger(self):
        return self._logger

    @property
    def db(self):
        return self._db

    #执行sql
    def execute(self, sql):
        try:
            self.cursor.execute(sql)
        except Exception as e:
            self.logger.error(traceback.print_exc())
            self.logger.error("Query error: %s", e.args)
            self.logger.error(sql)
            self.db.rollback()
        else:
            self.db.commit()

    #发布消息
    def public(self, msg):
        self.meta.publish(self.chan_pub, msg)
        return True

    #订阅消息
    def subscribe(self):
        pub = self.meta.pubsub()
        pub.subscribe(self.chan_sub)
        return pub

    #处理订阅信息
    def parsemsg(self, msg):
        if not isinstance(msg, dict):
            return
        key = msg.get('data', None)
        if not (isinstance(key, str) or isinstance(key, unicode)):
            return
        table, id = key.split(split_symbol)
        if config.VIDEO_COMMENT_TABLE_BASE_NAME in table:
            self.updatecomment(key, id)
        elif config.USER_TABLE_BASE_NAME in table:
            self.updateuser(key, id, table)
        elif config.VIDEO_TABLE_BASE_NAME in table:
            self.updatevideo(key, id)
        else:
            pass

    #更新video数据
    def updatevideo(self, key, vid):
        video = self.data.hgetall(key)
        if video:
            if video.get('like', None):
                video['`like`'] = video['like']
            update_video_sql = SQL_refector.video_update(vid, **video)
            # print update_video_sql
            self.execute(update_video_sql)
            self.data.delete(key)

    #更新user数据
    def updateuser(self, key, uid, tablename):
        pass

    #更新comment数据
    def updatecomment(self, key, cid):
        comment = self.data.hgetall(key)
        if comment:
            if comment.get('like', None):
                comment['`like`'] = comment['like']
            update_comment_sql = SQL_refector.videocomment_update(cid, **comment)
            self.execute(update_comment_sql)
            self.data.delete(key)

if __name__ == '__main__':
    redisconn = RedisPub()
    redissub = redisconn.subscribe()
    for msg in redissub.listen():
        print msg
        redisconn.parsemsg(msg)