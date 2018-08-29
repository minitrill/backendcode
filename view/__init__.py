#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/18 10:42
# @Author  : 曾凌峰
# @Site    : 
# @File    : __init__.py
# @Software: PyCharm

import tornado
import tornado.web
import datetime
import json

import errors

from tornado import gen
from models import User
from models import task

'''
|code| 含义          |
|----|--------------|
|0   |成功           |
|30  |资源不存在      |
|20  |资源已存在      |
|63  |没有权限请求该资源|
|54  |请求有误        |
'''

class CodeNum:
    SUCCESS = 0
    NORESOURCE = 30
    RESOURCEEXIST = 20
    PERMISSIONDENY = 63
    REQUESTERROR = 54

#基础返回格式
Baserespon = {
	'success' : True,
	'code' : 0, #错误码，0代表成功
	'data' : None,
	'message' : '成功'  #提示消息
}

#资源不存在返回格式
Nonerespon = {
    'success': False,
    'code': 30,  # 错误码，资源不存在
    'data': None,
    'message': '资源不存在'  # 提示消息
}

Badrespon = {
    'success': False,
    'code': 54,  # 错误码，请求有误
    'data': None,
    'message': '请求有误'  # 提示消息
}

#tcelery.setup_nonblocking_producer()

class Respon(dict):
    def __init__(self, respon=Baserespon, message=u'成功', data= None):
        if not isinstance(respon, dict):
            raise TypeError('respon should be dict type')
        super(Respon, self).__init__(respon)
        self['message'] = message.message if isinstance(message, Exception) else message
        self['data'] = data


class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "http://10.70.102.55:9090") # 这个地方可以写域名
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.set_header("Access-Control-Allow-Credentials", True)

    def post(self):
        self.write('some post')

    def get(self):
        self.write('some get')

    def options(self):
        # no body
        self.set_status(204)
        self.finish()

    # def get_current_user(self):
    #     return self.current_user()

    @property
    def db(self):
        """使用 self.db 调用 SQLClient 对象, 减少import"""
        return self.application.db

    @property
    def data(self):
        """使用 self.data 调用 DataMysql对象, 减少import"""
        return self.application.data

    @property
    def log(self):
        return self.application.log

    def get_current_user(self):
        uid = self.get_secure_cookie('uid')
        nickname = self.get_secure_cookie('nickname')
        account = self.get_secure_cookie('account')
        if uid and nickname and account:
            return User(uid=uid, nickname=nickname, account=account)
        else:
            return None

    def set_default_headers(self):
        """设置响应的默认 HTTP HEADER, 非全局
        """
        headers = dict(
            Server='MY_SERVER',
            Date=datetime.datetime.now()
        )
        for k, v in headers.items():
            self.set_header(k, v)
        cookies = dict(
            foo='foo_cookie',
            bar='bar_cookie'
        )
        for k, v in cookies.items():
            self.set_cookie(k, v, expires_days=7)

    def get_json(self):
        """获取json数据 注意获取到的数据都是unicode编码"""
        if "application/json" in self.request.headers["Content-Type"]:
            return json.loads(self.request.body)
        raise RuntimeError(errors.JSON_SHOULD_BE_NOT_NONE)

    def _request_summary(self):
        return "%s %s (%s) %s" % (self.request.method, self.request.uri,
               self.request.remote_ip, self.request.headers.get('User-Agent', ''))


class HelloWolrdHandler(BaseHandler):
    def get(self):
        self.finish('hello world')

class IndexHandler(BaseHandler):
    def get(self):
        self.render('index.html')

class TestHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        result = yield gen.Task(task.RecommendVideo.apply_async,
                                args = ['-5830510677343033396'])
        self.finish(Respon(Baserespon, data=result.result))

    def on_success(self, result):
        print result
        self.finish(Respon(Baserespon, data=result))


from authentication import *
from video import *
from social import *