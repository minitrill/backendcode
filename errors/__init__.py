#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/18 22:12
# @Author  : 曾凌峰
# @Site    : 
# @File    : __init__.py
# @Software: PyCharm


ACCOUNT_ALREADY_EXIST = u'当前账号已存在'

ACCOUNT_SHOULD_BE_NOT_NONE = u'账号不能为空'
PASSWORD_SHOULD_BE_NOT_NONE = u'密码不能为空'
NICKNAME_SHOULD_BE_NOT_NONE = u'昵称不能为空'
COMMENT_SHOULD_BE_NOT_NONE = u'评论内容不能为空'
MESSAGE_RECIVE_SHOULD_BE_NOT_NONE = u'私信接受者不能为空'
MESSAGE_TEXT_SHOULD_BE_NOT_NONE = u'私信内容不能为空'

ACCOUNT_RULE = u'账号不允许数字和字母以外符号，长度不少于6位'
PASSWORD_RULE = u'密码要求为数字字母组合，不小于8位'
NICKNAME_RULE = u'昵称不能包含敏感词，且长度不少于4位'

JSON_SHOULD_BE_NOT_NONE = u'JSON不能为空'

ACCOUNT_PASSWORD_ERROR = u'账号或密码错误'

ACCOUNT_BAN = u'该用户存在违规行为，请联系工作人员'

LOGIN_COOKIES_INVALID = u'当前没有登录信息'

API_PERMISSION_DENY = u'当前用户无法使用该接口'

PORTRAIT_SHOULD_BE_BASE64 = u'头像文件非base64编码'

VIDEO_NOT_FOUND = u'视频资源不存在'
COMMENT_NOT_FOUND = u'评论资源不存在'

ARGUMENT_FAULT = u'参数错误'

GEOINFORMATION_ERROR = u'请提交正确格式的地理信息'

NOT_NONE = {
    u'account': ACCOUNT_SHOULD_BE_NOT_NONE,
    u'nickname': NICKNAME_SHOULD_BE_NOT_NONE,
    u'password': PASSWORD_SHOULD_BE_NOT_NONE,
    u'comment': COMMENT_SHOULD_BE_NOT_NONE,
    u'recive_uid': MESSAGE_RECIVE_SHOULD_BE_NOT_NONE,
    u'text': MESSAGE_TEXT_SHOULD_BE_NOT_NONE
}

NAMING_RULE = {
    u'account': ACCOUNT_RULE,
    u'nickname': NICKNAME_RULE,
    u'password': PASSWORD_RULE,
}