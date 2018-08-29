#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/17 15:42
# @Author  : 曾凌峰
# @Site    : 
# @File    : authentication.py
# @Software: PyCharm

import tornado.web
import errors
import copy

from tornado import gen
from view import BaseHandler
from view import Baserespon, Nonerespon, Badrespon, Respon

class AuthenticationHandler(BaseHandler):
    #获取登录状态
    def get(self, *args, **kwargs):
        user = self.current_user
        if not user:
            self.finish(Respon(Badrespon, errors.LOGIN_COOKIES_INVALID))
        else:
            data = {
                'islogin': True,
                'account': user.account,
                'nickname': user.nickname,
                'id': user.uid
            }
            self.finish(Respon(Baserespon, data=data))

    #登录
    @gen.coroutine
    def post(self, *args, **kwargs):
        try:
            json = self.get_json()
            uid, nickname, account = yield self.data.check_user(**json)
            self.set_secure_cookie('uid', str(uid))
            self.set_secure_cookie('nickname', nickname)
            self.set_secure_cookie('account', account)
            self.finish(Baserespon)
        except Exception as e:
            self.finish(Respon(Badrespon, e))

    #登出
    @tornado.web.authenticated
    def delete(self, *args, **kwargs):
        self.clear_all_cookies()
        self.finish(Baserespon)

    #更新状态
    @tornado.web.authenticated
    def put(self, *args, **kwargs):
        pass

class RegistHandler(BaseHandler):
    #注册账号
    @gen.coroutine
    def post(self, *args, **kwargs):
        try:
            json = self.get_json()
            uid, nickname, account = yield self.data.create_user(**json)
            self.set_secure_cookie('uid', str(uid))
            self.set_secure_cookie('nickname', nickname)
            self.set_secure_cookie('account', account)
            self.finish(Baserespon)
        except Exception as e:
            self.finish(Respon(Badrespon, e))

    #获取个人信息
    @gen.coroutine
    @tornado.web.authenticated
    def get(self):
        try:
            user = self.current_user
            if not user:
                raise RuntimeError(errors.LOGIN_COOKIES_INVALID)
            data = yield self.data.get_user(user.uid)
            self.finish((Respon(Baserespon, data=data)))
        except Exception as e:
            self.finish(Respon(Badrespon, e))


class PortraitHandler(BaseHandler):
    #上传头像
    @gen.coroutine
    @tornado.web.authenticated
    def post(self):
        pass


class UserHandler(BaseHandler):
    #获取用户信息
    @gen.coroutine
    #@tornado.web.authenticated
    def get(self, uid):
        if not uid:
            self.finish(Respon(Nonerespon))
        else:
            try:
                data = yield self.data.get_user(uid)
                self.finish(Respon(Baserespon, data=data))
            except Exception as e:
                self.finish(Respon(Badrespon, e))