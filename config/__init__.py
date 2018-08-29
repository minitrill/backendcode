#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/16 17:05
# @Author  : 曾凌峰
# @Site    : 
# @File    : __init__.py
# @Software: PyCharm

from .default import Config
from .development import DevelopmentConfig
from .product import ProductConfig
from .static import Static

configs = {
    'default': Config,
    'development': DevelopmentConfig,
    'product': ProductConfig
}

config = configs['development']

static = Static