#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/16 17:05
# @Author  : 曾凌峰
# @Site    : 
# @File    : default.py
# @Software: PyCharm

import os

#获取当前脚本文件的绝对路径
basedir = os.path.abspath(os.path.dirname(__file__))

# 基本配置
class Config:
    # 端口号
    PORT = 5000

    # 设置秘钥，可用于各个扩展程序中
    COOKIE_SECRET = os.environ.get('SECRET_KEY') or 'minitrill2018'

    DEBUG = False
    XSRF_COOKIES = True
    GZIP = True
    # 后端代码路径 /data/minitrill/code/backend/
    ROOT_PATH = os.path.join(os.getcwd())
    # /data/minitrill/code
    CODE_PATH = os.path.dirname(ROOT_PATH)
    # 整个minitrill工程项目路径 /data/minitrill
    PROJECT_PATH = os.path.dirname(CODE_PATH)
    # /data
    DATA_PATH = os.path.dirname(PROJECT_PATH)
    STATIC_PATH = os.path.join(ROOT_PATH, 'static')
    TEMPLATE_PATH = os.path.join(ROOT_PATH, 'template')
    UPLOAD_PATH = os.path.join(STATIC_PATH, 'upload')
    LOG_PATH = os.path.join(ROOT_PATH, 'log')

    USER_PATH = os.path.join(PROJECT_PATH, 'user')
    PORTRAIT_PATH = os.path.join(USER_PATH, 'photo')

    TORNADOACCESS_LOG = os.path.join(LOG_PATH, 'access.log')
    BEHAVIOUR_LOG = os.path.join(LOG_PATH, 'behavior.log')

    MYSQL_LOGGER = 'sqllogger'


