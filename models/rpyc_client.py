#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/14 20:23
# @Author  : 曾凌峰
# @Site    : 
# @File    : rpyc_client.py
# @Software: PyCharm

import rpyc
import utils
import atexit

class RpycConnectError(Exception):
    pass

class RpycController(object):
    __metaclass__ = utils.Singleton
    def __init__(self, config):
        self.host = config.RPYC_HOST
        self.port = config.RPYC_PORT
        self.connect()
        #atexit.register(self.onDisconnect())

    def connect(self, portRange=10):
        #rpyc服务器会在端口号被占用的情况下自动+1尝试在新的端口号服务，设置portrange增加健壮性
        for i in xrange(portRange):
            try:
                self.conn = rpyc.connect(self.host, port=i + self.port)
                self.closed = False
                break
            except Exception, e:
                print e
        else:
            raise RpycConnectError('rpyc connect error')

    @property
    def connected(self):
        return self.conn and not self.conn.closed

    def onDisconnect(self):
        self.conn.close()

    # 这个重载的作用是可以更方便,更自然地访问remote module
    # r.com.data.cdata <=> r.root.com.data.cdata
    def __getattr__(self, key):
        if self.conn:
            try:
                return self.conn.root.__getattr__(key)
            except (EOFError, ReferenceError, AttributeError):
                #重新连接
                self.conn.close()
                self.connect()
                return self.conn.root.__getattr__(key)
        else:
            return None

    # 这两个重载的作用是可以更方便的访问remote的namespace
    # 例如:self['a'] <=> self.conn.namespace['a']
    def __getitem__(self, key):
        return self.conn.namespace[key]

    def __setitem__(self, key, value):
        self.conn.namespace[key] = value


if __name__ == '__main__':
    remote = RpycController('139.199.183.30', 11511)
    for i in range(10):
        print remote.cmd('-5830510677343033396')