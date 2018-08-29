#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/24 14:41
# @Author  : 曾凌峰
# @Site    : 
# @File    : social.py
# @Software: PyCharm

import tornado.web
import errors

from tornado.web import gen
from view import BaseHandler
from view import Nonerespon, Baserespon, Badrespon, Respon

class VideoShareHandler(BaseHandler):
    @gen.coroutine
    @tornado.web.authenticated
    def put(self, video_id):
        try:
            yield self.data.share_video(video_id)
            self.finish(Baserespon)
        except Exception as e:
            self.finish(Respon(Badrespon, message=e))


class VideoLikeHandler(BaseHandler):
    @gen.coroutine
    @tornado.web.authenticated
    def put(self, video_id):
        try:
            yield self.data.like_video(video_id)
            self.finish(Baserespon)
        except Exception as e:
            self.finish(Respon(Badrespon, message=e))


class RelationHandler(BaseHandler):
    #关注某人
    @gen.coroutine
    @tornado.web.authenticated
    def post(self, user_id):
        try:
            user = self.current_user
            yield self.data.focus_user(user_id, user.uid)
            self.finish(Baserespon)
        except Exception as e:
            self.finish(Respon(Badrespon, message=e))

    #取消关注某人
    @gen.coroutine
    @tornado.web.authenticated
    def delete(self, user_id):
        try:
            user = self.current_user
            yield self.data.defocus_user(user_id, user.uid)
            self.finish(Baserespon)
        except Exception as e:
            self.finish(Respon(Badrespon, message=e))

    #获取自己关注的人或者粉丝的信息
    @gen.coroutine
    @tornado.web.authenticated
    def get(self, user_id):
        try:
            type = self.get_argument('type', 'fan')
            page = int(self.get_argument('page', 1))-1 #数据第0页开始
            user = self.current_user
            if not user:
                raise RuntimeError(errors.LOGIN_COOKIES_INVALID)
            if type == 'fan':
                data = yield self.data.get_fanuser(user.uid, page)
            elif type == 'master':
                data = yield self.data.get_masteruser(user.uid, page)
            elif type == 'isfollow':
                data = yield self.data.isfollow(user_id, user.uid)
            else:
                data= None
            self.finish(Respon(Baserespon, data=data))
        except Exception as e:
            self.finish(Respon(Badrespon, message=e))


class MessageHandler(BaseHandler):
    #发送私信
    @gen.coroutine
    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        try:
            user = self.current_user
            json = self.get_json()
            if not user:
                raise RuntimeError(errors.LOGIN_COOKIES_INVALID)
            yield self.data.insert_message(user.uid, **json)
            self.finish(Baserespon)
        except Exception as e:
            self.finish(Respon(Badrespon, message=e))

    #获取私信
    @gen.coroutine
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        try:
            type = self.get_argument('type', 'send')
            page = int(self.get_argument('page', 1)) - 1  # 数据第0页开始
            user = self.current_user
            if not user:
                raise RuntimeError(errors.LOGIN_COOKIES_INVALID)
            if type == 'send':
                data = yield self.data.get_send_message(user.uid, page)
            elif type == 'recive':
                data = yield self.data.get_recive_message(user.uid, page)
            elif type == 'unreadnum':
                data = yield self.data.unread_messagenum(user.uid)
            else:
                data=None
            self.finish(Respon(Baserespon, data=data))
        except Exception as e:
            self.finish(Respon(Badrespon, message=e))

    #把私信标记为已读
    @gen.coroutine
    @tornado.web.authenticated
    def put(self, messageid):
        try:
            yield self.data.read_message(messageid)
            self.finish(Baserespon)
        except Exception as e:
            self.finish(Respon(Badrespon, message=e))

    #删除私信
    @gen.coroutine
    @tornado.web.authenticated
    def delete(self, messageid):
        try:
            yield self.data.delete_message(messageid)
            self.finish(Baserespon)
        except Exception as e:
            self.finish(Respon(Badrespon, message=e))


class ChatHandler(BaseHandler):
    @gen.coroutine
    @tornado.web.authenticated
    def post(self):
        try:
            json = self.get_json()
            if not json:
                raise RuntimeError(errors.JSON_SHOULD_BE_NOT_NONE)
            message = json.get('message', '')
            reply = ''
            if message == '你好':
                reply = '你好呀~'
            elif message == '你来过这里吗？你拍的视频好有意思':
                pass
            self.finish(Respon(Baserespon, data=reply))
        except Exception as e:
            self.finish(Respon(Badrespon, message=e))