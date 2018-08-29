#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/20 21:59
# @Author  : 曾凌峰
# @Site    : 
# @File    : video.py
# @Software: PyCharm

import tornado.web
import errors

from tornado.web import gen
from view import BaseHandler
from view import Nonerespon, Baserespon, Badrespon, Respon
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor


class RecommendVideoHandler(BaseHandler):
    executor = ThreadPoolExecutor(4)

    @run_on_executor
    def recommend_video(self, uid):
        if isinstance(uid, unicode):
            uid = uid.encode('utf8')
        result = self.application.remote.cmd(uid)
        return [str(vid) for vid in list(result)]

    @gen.coroutine
    #@tornado.web.authenticated
    def get(self):
        try:
            # user = self.current_user
            # if user:
            #     vids = yield self.recommend_video('-5104583026337327941')
            # else:
            #     vids = yield self.recommend_video('-5104583026337327941')
            vids = ['6584690495409097991', '6584398245387046147', '6570100343449849092',\
                    '6584573083351256327', '6580138391453568264', '6502363396086697229',\
                    '6569537911270673677', '6585385921045073159', '6584251747315748109',\
                    '6584626231122070798']
            if vids:
                data = yield self.data.get_videoswithvids(vids)
            else:
                data = yield self.data.get_videos(page=0)
            self.finish(Respon(Baserespon, data=data))
        except Exception as e:
            self.finish(Respon(Badrespon, message=e))


class VideoHandler(BaseHandler):
    @gen.coroutine
    #@tornado.web.authenticated
    def get(self, video_id):
        try:
            if not video_id:
                page = int(self.get_argument('page', 1))-1 #数据第0页开始
                uid = self.get_argument('uid', None)
                if not uid:
                    data = yield self.data.get_videos(page)
                else:
                    data = yield self.data.get_videos_uid(uid, page)
            else:
                data= yield self.data.get_video(video_id)
            self.finish(Respon(Baserespon, data=data))
        except Exception as e:
            self.finish(Respon(Badrespon, message=e))


class VideoTagHandler(BaseHandler):
    @gen.coroutine
    #@tornado.web.authenticated
    def get(self):
        data = yield self.data.get_videotag()
        self.finish(Respon(Baserespon, data=data))


class NeighbourVideoHandler(BaseHandler):
    @gen.coroutine
    #@tornado.web.authenticated
    def get(self):
        try:
            longitude = self.get_argument('longitude', None)
            latitude = self.get_argument('latitude', None)
            level = self.get_argument('level', 8)
            page = int(self.get_argument('page', 1)) - 1  # 数据第0页开始
            if longitude and latitude and level:
                data = yield self.data.get_videoswithneighbour(longitude, latitude, level, page)
                self.finish(Respon(Baserespon, data=data))
            else:
                self.finish(Respon(Nonerespon))
        except Exception as e:
            self.finish(Respon(Badrespon, e))


class FavoriteTagHandler(BaseHandler):
    #提交个人喜爱的视频标签
    @gen.coroutine
    @tornado.web.authenticated
    def post(self):
        try:
            user = self.current_user
            json = self.get_json()
            data = yield self.data.insert_favoritetag(user, **json)
            self.finish(Respon(Baserespon, data=data))
        except Exception as e:
            self.finish(Respon(Badrespon, e))

    #获取个人喜爱的视频标签
    @gen.coroutine
    @tornado.web.authenticated
    def get(self):
        try:
            user = self.current_user
            data = yield self.data.get_favoritetagname(user)
            self.finish(Respon(Baserespon, data=data))
        except Exception as e:
            self.finish(Respon(Badrespon, e))

    #修改个人喜爱的视频标签
    @gen.coroutine
    @tornado.web.authenticated
    def put(self):
        pass


class VideoCommentHandler(BaseHandler):
    #创建评论
    @gen.coroutine
    @tornado.web.authenticated
    def post(self, video_id):
        try:
            user = self.current_user
            json = self.get_json()
            if user is None:
                raise RuntimeError(errors.LOGIN_COOKIES_INVALID)
            if not video_id:
                raise ValueError(errors.VIDEO_NOT_FOUND)
            yield self.data.insert_videocomment(video_id, user.uid, **json)
            self.finish(Baserespon)
        except Exception as e:
            self.finish(Respon(Badrespon, message=e))

    #获取评论
    @gen.coroutine
    #@tornado.web.authenticated
    def get(self, video_id):
        try:
            if not video_id:
                raise ValueError(errors.VIDEO_NOT_FOUND)
            data = yield self.data.get_videocomment(video_id)
            self.finish(Respon(Baserespon, data=data))
        except Exception as e:
            self.finish(Respon(Badrespon, message=e))


class CommentHandler(BaseHandler):
    #删除某条评论
    @gen.coroutine
    @tornado.web.authenticated
    def delete(self, commentid):
        try:
            if not commentid:
                raise ValueError(errors.COMMENT_NOT_FOUND)
            yield self.data.delete_videocomment(commentid)
            self.finish(Baserespon)
        except Exception as e:
            self.finish(Respon(Badrespon, message=e))

    #点赞某条评论
    @gen.coroutine
    @tornado.web.authenticated
    def put(self, commentid):
        try:
            if not commentid:
                raise ValueError(errors.COMMENT_NOT_FOUND)
            yield self.data.update_like_videocomment(commentid)
            self.finish(Baserespon)
        except Exception as e:
            self.finish(Respon(Badrespon, message=e))