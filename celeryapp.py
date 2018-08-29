#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/6 10:30
# @Author  : 曾凌峰
# @Site    :
# @File    : celeryapp.py
# @Software: PyCharm

"""
运行方式：
celery worker -A celeryapp.celery -l INFO
"""

from celery import platforms
from models import celery


#加上这一行允许root用户运行celery
#如果无效则 export C_FORCE_ROOT="true"
platforms.C_FORCE_ROOT = True

