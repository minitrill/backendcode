#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/20 13:12
# @Author  : 曾凌峰
# @Site    : 
# @File    : model.py
# @Software: PyCharm

class User(object):
    '''
    用户模型
    '''
    def __init__(self, **kwargs):
        #uid, nickname, account都是str类型的，不是unicode
        self.uid = kwargs.get('uid', None)
        self.nickname = kwargs.get('nickname', None)
        self.account = kwargs.get('account', None)

    def __nonzero__(self):
        return bool(self.uid and self.nickname and self.account)


