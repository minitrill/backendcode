#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/17 18:13
# @Author  : 曾凌峰
# @Site    : 
# @File    : static.py
# @Software: PyCharm

import utils
import hashlib

"""
数据库说明:
表名
"""
class Static(object):
    __metaclass__ = utils.Singleton

    SYS_DATABASE_NAME = None  # 系统数据库名
    USER_TABLE_BASE_NAME = None  # 用户表
    VIDEO_TABLE_BASE_NAME = None  # 视频资源表
    VIDEO_TAG_TABLE_BASE_NAME = None  # 视频标签表
    USER_RELATION_TABLE_BASE_NAME = None  # 用户关系表
    MESSAGE_TABLE_BASE_NAME = None  # 私信表
    VIDEO_COMMENT_TABLE_BASE_NAME = None  # 视频评论表
    VIDEO_LIKE_TABLE_BASE_NAME = None  # 视频点赞表
    USER_VIDEO_TAG_TABLE_BASE_NAME = None  # 用户喜爱的视频标签表

    def __init__(self, config):
        self.static_value_init(config)

    def static_value_init(self, config):
        Static.config = config
        Static.SYS_DATABASE_NAME = config.TORMYSQL_DB
        Static.USER_TABLE_BASE_NAME = config.USER_TABLE_BASE_NAME
        Static.VIDEO_TABLE_BASE_NAME = config.VIDEO_TABLE_BASE_NAME
        Static.VIDEO_TAG_TABLE_BASE_NAME = config.VIDEO_TAG_TABLE_BASE_NAME
        Static.USER_RELATION_TABLE_BASE_NAME = config.USER_RELATION_TABLE_BASE_NAME
        Static.MESSAGE_TABLE_BASE_NAME = config.MESSAGE_TABLE_BASE_NAME
        Static.VIDEO_COMMENT_TABLE_BASE_NAME = config.VIDEO_COMMENT_TABLE_BASE_NAME
        Static.VIDEO_LIKE_TABLE_BASE_NAME = config.VIDEO_LIKE_TABLE_BASE_NAME
        Static.USER_VIDEO_TAG_TABLE_BASE_NAME = config.USER_VIDEO_TAG_TABLE_BASE_NAME

    # @staticmethod
    # def get_table_num(hash_value):
    #     """根据hash值获取分表号"""
    #     if -9223372036854775807 <= hash_value < -7393347003251626769:
    #         return 1
    #     elif -7393347003251626769 <= hash_value < -5544820905583124692:
    #         return 2
    #     elif -5544820905583124692 <= hash_value < -3703662328893783636:
    #         return 3
    #     elif -3703662328893783636 <= hash_value < -1864090509109668823:
    #         return 4
    #     elif -1864090509109668823 <= hash_value < -25556603170130521:
    #         return 5
    #     elif -25556603170130521 <= hash_value < 1829170723854020188:
    #         return 6
    #     elif 1829170723854020188 <= hash_value < 3671409183307186906:
    #         return 7
    #     elif 3671409183307186906 <= hash_value < 5513089284982408107:
    #         return 8
    #     elif 5513089284982408107 <= hash_value < 7373459306470554807:
    #         return 9
    #     elif 7373459306470554807 <= hash_value < 9233372036854775808:
    #         return 10
    #     else:  # 越界
    #         raise IndexError("Unexpect hash value" + str(hash_value))

    # @staticmethod
    # def get_table_num(hash_value):
    #     """根据hash值获取分表号"""
    #     if 1 <= hash_value < 7175544031534253687:
    #         return 1
    #     elif 7175544031534253687 <= hash_value < 14351088063068507374:
    #         return 2
    #     elif 14351088063068507374 <= hash_value < 21526632094602761061:
    #         return 3
    #     elif 21526632094602761061 <= hash_value < 28702176126137014749:
    #         return 4
    #     elif 28702176126137014749 <= hash_value < 35877720157671268436:
    #         return 5
    #     elif 35877720157671268436 <= hash_value < 43053264189205522123:
    #         return 6
    #     elif 43053264189205522123 <= hash_value < 50228808220739775811:
    #         return 7
    #     elif 50228808220739775811 <= hash_value < 57404352252274029498:
    #         return 8
    #     elif 57404352252274029498 <= hash_value < 64579896283808283185:
    #         return 9
    #     elif 64579896283808283185 <= hash_value < 71755440315342536873:
    #         return 10
    #     else:  # 越界
    #         raise IndexError("Unexpect hash value" + str(hash_value))

    @staticmethod
    def get_table_num(hash_value):
        """根据hash值获取分表号
        1276478784635844147
        """
        hash_value = int(hash_value)
        if -6382393923179220736 <= hash_value < -5105915138543376589:
            return 1
        elif -5105915138543376589 <= hash_value < -3829436353907532442:
            return 2
        elif -3829436353907532442 <= hash_value < -2552957569271688295:
            return 3
        elif -2552957569271688295 <= hash_value < -1276478784635844148:
            return 4
        elif -1276478784635844148 <= hash_value < -1:
            return 5
        elif -1 <= hash_value < 1276478784635844146:
            return 6
        elif 1276478784635844146 <= hash_value < 2552957569271688293:
            return 7
        elif 2552957569271688293 <= hash_value < 3829436353907532440:
            return 8
        elif 3829436353907532440 <= hash_value < 5105915138543376587:
            return 9
        elif 5105915138543376587 <= hash_value < 6382393923179220735:
            return 10
        else:  # 越界
            raise IndexError("Unexpect hash value" + str(hash_value))

    @staticmethod
    def get_hash(account):
        """
        在项目进行过程中，由于linux和windows环境的python的hash函数的结果不同，导致问题越来越多，为了方便
        开发和测试，开发是在windows环境，测试和最终是在linux环境，这里决定使用md5，除留取余法，自己构造
        一个两个平台通用的hash函数
        """
        m = hashlib.md5()
        m.update(account)
        digest = m.hexdigest()
        number = int(digest, 16)
        return (number % 12764787846358441471) - 6382393923179220736