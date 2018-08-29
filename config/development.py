#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/16 17:05
# @Author  : 曾凌峰
# @Site    : 
# @File    : development.py
# @Software: PyCharm

import os

from kombu import Queue

from .default import Config

class DevelopmentConfig(Config):
    # mysql地址
    TORMYSQL_HOST = '118.126.104.182'
    # mysql端口号
    TORMYSQL_PORT = 3306
    # mysql用户名
    TORMYSQL_USER = 'root'
    # mysql密码
    TORMYSQL_PASSWORD = '19950705'
    # 数据库
    TORMYSQL_DB = 'minitrill'
    # 字符集
    DEFAULTCHARSET  = 'utf8'
    # 最大连接数
    MAX_CONNECTION = 20
    # idle timeout
    IDLE_SECONDS = 7200
    # 最大timeout次数
    WAIT_TIMEOUT_SECONDS = 3
    # 日志文件
    TORMYSQL_LOG = os.path.join(Config.LOG_PATH, 'sqlclient.log')

    REDIS_HOST = '47.106.158.125'
    REDIS_PORT = 6379
    REDIS_SELECT_DB = 5 #主要数据库
    REDIS_META_DB = 6 #元数据库 维护1中数据的信息
    REDIS_PASSWORD = 'selected_db'

    USER_TABLE_BASE_NAME = 'User'  # 用户表
    VIDEO_TABLE_BASE_NAME = 'Video'  # 视频资源表
    VIDEO_TAG_TABLE_BASE_NAME = 'VideoTag'  # 视频标签表
    USER_RELATION_TABLE_BASE_NAME = 'UserRelation'  # 用户关系表
    MESSAGE_TABLE_BASE_NAME = 'Message'  # 私信表
    VIDEO_COMMENT_TABLE_BASE_NAME = 'VideoComment'  # 视频评论表
    VIDEO_LIKE_TABLE_BASE_NAME = 'VideoLike'  # 视频点赞表
    USER_VIDEO_TAG_TABLE_BASE_NAME = 'UserTag'  # 用户喜爱的视频标签表

    # celery的配置
    CELERY_BROKER_URL = 'amqp://root:root@47.106.158.125:5672/minitrill'
    CELERY_BACKEND = 'amqp://root:root@47.106.158.125:5672/'


    #rpyc配置
    RPYC_HOST = '139.199.183.30'
    RPYC_PORT = 11511

    USER_RELATION_PERPAGE = 10 #用户关系表分页查询数量
    VIDEO_PERPAGE = 5 #每次取5条视频
    # VIDEO_COMMENT_PERPAGE = 20
    MESSAGE_PERPAGE = 10 #每页私信数量