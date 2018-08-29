#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/24 16:03
# @Author  : 曾凌峰
# @Site    : 
# @File    : redis_client.py
# @Software: PyCharm

import utils
import tornadoredis
import redis

class RedisClient(object):
    __metaclass__ = utils.Singleton
    def __init__(self, config):
        self._config = config
        self._datapool = redis.ConnectionPool(max_connections=20, host=self._config.REDIS_HOST, port=self._config.REDIS_PORT,\
                        db=self._config.REDIS_SELECT_DB, decode_responses=True)
        self._metapool = redis.ConnectionPool(max_connections=20, host=self._config.REDIS_HOST, port=self._config.REDIS_PORT,\
                        db=self._config.REDIS_META_DB, decode_responses=True)

    #data层
    @property
    def data(self):
        return redis.Redis(connection_pool=self._datapool)

    #meta层
    @property
    def meta(self):
        return redis.Redis(connection_pool=self._metapool)


if __name__ == '__main__':
    #不能这样测试，tornadoredis一定要配合tornado使用
    pool = tornadoredis.ConnectionPool(max_connections=500, wait_for_available=True)
    cli = tornadoredis.Client(host='47.106.158.125', port=6379, selected_db=0, connection_pool=pool)
    abc = cli.get('abc')
    print 'hello'
    print abc