#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/16 19:34
# @Author  : 曾凌峰
# @Site    : 
# @File    : application.py
# @Software: PyCharm

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
#import tcelery

from config import config, static
from models import SQLClient, Data, RpycController, Cache
from log import MinitrillLog

from view import AuthenticationHandler, RegistHandler, HelloWolrdHandler, UserHandler, FavoriteTagHandler, PortraitHandler
from view import VideoTagHandler, VideoHandler, VideoCommentHandler, CommentHandler, NeighbourVideoHandler, RecommendVideoHandler
from view import VideoShareHandler, VideoLikeHandler, RelationHandler, MessageHandler, IndexHandler,TestHandler, ChatHandler

#tcelery.setup_nonblocking_producer()

HANDLERS = [
    (r'/', IndexHandler),
    (r'/user/.*', IndexHandler),
    (r'/citywide', IndexHandler),
    (r'/test', TestHandler),
    (r'/video', RecommendVideoHandler),
    (r'/helloworld', HelloWolrdHandler),
    (r'/api/v1.0/session', AuthenticationHandler),
    (r'/api/v1.0/account', RegistHandler),
    (r'/api/v1.0/user/(0*|[1-9][0-9]*|-[1-9][0-9]*)', UserHandler),
    (r'/api/v1.0/video/tag', VideoTagHandler),
    (r'/api/v1.0/video/(\d*)', VideoHandler),
    (r'/api/v1.0/neighbour/video', NeighbourVideoHandler),
    (r'/api/v1.0/video/favoritetag', FavoriteTagHandler),
    (r'/api/v1.0/account/portrait', PortraitHandler),
    (r'/api/v1.0/video/share/(\d*)', VideoShareHandler),
    (r'/api/v1.0/video/like/(\d*)', VideoLikeHandler),
    (r'/api/v1.0/video/videocomment/(0*|[1-9][0-9]*|-[1-9][0-9]*)', VideoCommentHandler),
    (r'/api/v1.0/videocomment/(\d*)', CommentHandler),
    (r'/api/v1.0/relation/(0*|[1-9][0-9]*|-[1-9][0-9]*)', RelationHandler),
    (r'/api/v1.0/message/(0*|[1-9][0-9]*|-[1-9][0-9]*)', MessageHandler),
    (r'/api/v1.0/conversation', ChatHandler),
]


def createApp():
    SETTINGS = {
        "static_path": config.STATIC_PATH,
        "template_path": config.TEMPLATE_PATH,
        "cookie_secret": config.COOKIE_SECRET,
        "login_url": "/login",
        #"xsrf_cookies": config[default].XSRF_COOKIES,
        "debug": config.DEBUG,
        "gzip": config.GZIP,
    }

    app = tornado.web.Application(
        handlers=HANDLERS,
        **SETTINGS
    )
    app.config = config
    app.remote = RpycController(app.config)
    app.db = SQLClient(config)
    app.cache = Cache(config)
    app.data = Data(app.db, app.cache, app.remote)
    app.static = static(app.config)
    MinitrillLog.log_init(app)
    return app


tornado.options.parse_command_line()
app = createApp()



if __name__ == '__main__':
    server = tornado.httpserver.HTTPServer(app)
    server.listen(8080)
    tornado.ioloop.IOLoop.current().start()
