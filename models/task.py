#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/6 11:15
# @Author  : 曾凌峰
# @Site    : 
# @File    : task.py
# @Software: PyCharm


from config import config
from celery import Celery, platforms
from rpyc_client import RpycController

#root用户运行
platforms.C_FORCE_ROOT = True


broker = config.CELERY_BROKER_URL
backend = config.CELERY_BACKEND

celery = Celery('tasks', broker=broker, backend=backend)
celery.conf.update(
    CELERY_ACCEPT_CONTENT =  ['pickle', 'json'],
    CELERY_RESULT_SERIALIZER = 'json',
    CELERY_TASK_SERIALIZER = 'json',
    CELERY_TIMEZONE = 'Asia/Makassar'
)

rpc_client = RpycController(config)

#已弃用，celery来执行远程调用的结果返回速度偏慢
@celery.task
def RecommendVideo(uid):
    """
    :return: 远程调用的结果
    """
    if isinstance(uid, unicode):
        uid = uid.encode('utf8')
    result = rpc_client.cmd(uid)
    return [str(vid) for vid in list(result)]
