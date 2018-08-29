#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/17 14:44
# @Author  : 曾凌峰
# @Site    : 
# @File    : sql_generator.py
# @Software: PyCharm

import utils

from config import static, config

class SQL_refector(object):
    __metaclass__ = utils.Singleton

    #以下数据顺序不可改动，要添加新列可加在尾部
    User_fields = ('uid', 'status', 'nickname', 'photo_url', 'account', 'password', 'sex', 'age', 'birth',\
                  'tel', 'country', 'province', 'city', 'brief_introduction', 'register_date', 'follow', \
                   'fans', 'video_num', 'video_like_num')

    Video_fields = ('vid', 'title', 'status', 'flag', 'uploader_uid', 'uploader_nickname', 'note', 'tag',\
                    '`like`', 'share', 'view', 'comment', 'upload_time', 'tag1_id', 'tag2_id', 'tag3_id',\
                    'v_url', 'v_photo_url', 'latitude', 'longitude', 'geohash', 'address', 'douyin_url')

    UserRelation_fields = ('relation_id', 'master_uid', 'fans_uid', 'relation_time')

    VideoComment_fields = ('comment_id', 'vid', 'uid', 'status', 'comment', 'ref_comment_id', 'comment_like', \
                           'comment_time', 'user_nickname', 'user_photo_url')

    Message_fields = ('message_id', 'status', 'send_uid', 'recive_uid', 'text', 'send_time', 'isread')

    def __init__(self):
        pass

    @staticmethod
    def clear_table(table_name):
        """
        :param table_name: 要清空的表名
        :return: 清空整张表的SQL
        """
        return """TRUNCATE {table}""".format(table=table_name)

    @staticmethod
    def user_get(account):
        """
        :param account:
        :return: 查找account是否存在的SQL，根据account的hash值查找
        """
        # 先不考虑分表分库的问题，只在一个库里查找
        account_hash = static.get_hash(account)
        tablenum = static.get_table_num(account_hash)
        SQL = """SELECT {fields} FROM {tbn} WHERE uid = \"{acth}\"""".format(
            fields=','.join(SQL_refector.User_fields), tbn=config.USER_TABLE_BASE_NAME+'_'+str(tablenum), acth=account_hash
        )
        return SQL

    @staticmethod
    def user_getwithid(userid):
        tablenum = static.get_table_num(userid)
        SQL = """SELECT {fields} FROM {tbn} WHERE uid = \"{uid}\"""".format(
            fields=','.join(SQL_refector.User_fields), tbn=config.USER_TABLE_BASE_NAME + '_' + str(tablenum),
            uid=userid
        )
        return SQL

    @staticmethod
    def user_insert(**kwargs):
        """
        :param kwargs: 属性字典
        :return: 注册插入用户数据的SQL
        """
        SQL = """INSERT INTO {tbn} SET """
        setvalue = []
        for key in SQL_refector.User_fields:
            if kwargs.get(key, None) is None:
                continue
            setvalue.append(key + '="{' + key + '}"')
        SQL = (SQL+','.join(setvalue)).decode('utf8').format(**kwargs)
        return SQL

    @staticmethod
    def user_update(userid, **kwargs):
        """
        :param userid: 用户id
        :param kwargs: 要更新的字段
        :return:
        """
        SQL = """UPDATE {tbn} SET """
        setvalue = []
        for key in SQL_refector.User_fields:
            if kwargs.get(key, None) is None:
                continue
            setvalue.append(key + '="{' + key + '}"')
        tablenum = static.get_table_num(userid)
        tablename = config.USER_TABLE_BASE_NAME+'_'+str(tablenum)
        kwargs['tbn']=tablename
        SQL = (SQL + ','.join(setvalue)+""" WHERE uid={uid}""".format(uid=userid)).decode('utf8').format(**kwargs)
        return SQL

    @staticmethod
    def user_incr_follow_fan(uid, followamount=0, fanamount=0):
        tablenum = static.get_table_num(uid)
        tablename = config.USER_TABLE_BASE_NAME + '_' + str(tablenum)
        followamount = str(followamount)
        fanamount = str(fanamount)
        SQL = """UPDATE {tbn} SET follow=follow+{_follow}, fan=fan+{_fan} WHERE uid={_uid}""".format(_fan=fanamount, \
                 _follow=followamount, _uid=uid, tbn=tablename)
        return SQL

    @staticmethod
    def videotag_get():
        """
        :return: 获取所有videotag的SQL
        """
        SQL = """SELECT tag_id, tag_name, tag_key_word, update_time FROM {tbn} """.\
            format(tbn = config.VIDEO_TAG_TABLE_BASE_NAME)
        return SQL

    @staticmethod
    def videos_get(page=0):
        """
        :return: 分页获取videos的SQL
        """
        # TODO 缺乏利用索引大小的优化
        # TODO 未对status和flag进行筛选
        SQL = """SELECT {video_fields} FROM {tbn} LIMIT {limitbound} , {limitnum}""".format(video_fields=','.\
             join(SQL_refector.Video_fields), tbn=config.VIDEO_TABLE_BASE_NAME, limitbound=page*config.VIDEO_PERPAGE,\
                        limitnum=config.VIDEO_PERPAGE)
        return SQL

    @staticmethod
    def videos_getwithuid(uid, page=0):
        """
        :param uid: 用户id
        :param page: 分页
        :return: 分页获取某个用户上传的videos的SQL
        """
        SQL = """SELECT {video_fields} FROM {tbn} WHERE uploader_uid={userid} LIMIT {limitbound},{limitnum}""".format(video_fields=','.\
             join(SQL_refector.Video_fields), tbn=config.VIDEO_TABLE_BASE_NAME, limitbound=page*config.VIDEO_PERPAGE,\
                        limitnum=config.VIDEO_PERPAGE, userid=uid)
        return SQL

    @staticmethod
    def videos_getwithgeo(neighbours, level, page=0):
        """
        :param neighbours: 临近的geohash
        :param level: 匹配的长度
        :return: 查找附近视频的SQL
        """
        # TODO 缺乏利用索引大小的优化
        # TODO 未对status和flag进行筛选
        SQL = """SELECT {video_fields} FROM {tbn} WHERE LEFT(`geohash`,{level}) IN ({geolist}) LIMIT {limitbound} , {limitnum}""".format(video_fields=','.join(
            SQL_refector.Video_fields), tbn=config.VIDEO_TABLE_BASE_NAME, limitbound=page * config.VIDEO_PERPAGE, limitnum=config.VIDEO_PERPAGE, level=level,\
            geolist=','.join(['\"' + nb + '\"' for nb in neighbours]))
        return SQL

    @staticmethod
    def video_get(vid):
        """
        :return: 获取video的SQL
        """
        # TODO 未对status和flag进行筛选
        SQL = """SELECT {video_fields} FROM {tbn} WHERE vid = \"{v_id}\"""".format(video_fields=','.join(SQL_refector.Video_fields),\
                   tbn=config.VIDEO_TABLE_BASE_NAME, v_id=vid)
        return SQL

    @staticmethod
    def videos_getwithvids(vids):
        """
        :param vids:vid列表
        :return: 获取多个video的sql
        """
        SQL = """SELECT {video_fields} FROM {tbn} WHERE vid in ({v_id})""".format(
            video_fields=','.join(SQL_refector.Video_fields), \
            tbn=config.VIDEO_TABLE_BASE_NAME, v_id=','.join(vids))
        return SQL

    @staticmethod
    def video_update(videoid, **kwargs):
        """
        :param videoid: video数据的id
        :param kwargs: 需要更新的字段和数据
        :return:更新video数据的SQL
        """
        SQL = """UPDATE {tbn} SET """.format(tbn=config.VIDEO_TABLE_BASE_NAME)
        setvalue = []
        for key in SQL_refector.Video_fields:
            if kwargs.get(key, None) in (None, 'None'):
                continue
            setvalue.append(key + '="{' + key + '}"')
        SQL = (SQL + ','.join(setvalue) + """ WHERE vid=\"{v_id}\"""".format(v_id=videoid)).decode('utf8').format(**kwargs)
        return SQL

    @staticmethod
    def video_incr_share_view_like(vid, shareamount=0, viewamount=0, likeamount=0):
        shareamount = str(shareamount)
        viewamount = str(viewamount)
        likeamount = str(likeamount)
        SQL = """UPDATE {tbn} SET share=share+{_share}, view=view+{_view}, `like`=`like`+{_like} WHERE vid={_vid}""".format(_share=shareamount,\
                        _view=viewamount, _vid=vid, tbn=config.VIDEO_TABLE_BASE_NAME, _like=likeamount)
        return SQL

    @staticmethod
    def favoritetag_get(uid='', tagid=''):
        """
        :return: 获取符合要求的所有喜爱视频标签的SQL
        """
        # MySQL 优化:
        # 使用 LIKE 而不使用 REGEXP
        # 在基于索引的情况下,模糊查询的左匹配(LIKE 'x%')的效率大于正则表达(REGEXP '^x')
        SQL = """SELECT uid, tagid FROM {tbn} WHERE uid LIKE \"%{u_id}%\" AND tagid LIKE \"%{tag_id}%\"""".\
            format(tbn = config.USER_VIDEO_TAG_TABLE_BASE_NAME, u_id=uid, tag_id=tagid)
        return SQL

    #由于涉及中文处理，该sql语句返回unicode格式
    @staticmethod
    def favoritetag_insert(uid, tagname):
        """
        :return: 插入喜爱视频标签的SQL
        """
        SQL = u"""INSERT INTO {usertag_tbn} (tagid, uid) SELECT tag_id, {u_id} FROM {videotag_tbn} WHERE tag_name=\"{tag_name}\"""".\
            format(usertag_tbn = config.USER_VIDEO_TAG_TABLE_BASE_NAME, videotag_tbn = config.VIDEO_TAG_TABLE_BASE_NAME,\
                   u_id=uid, tag_name=tagname)
        return SQL

    @staticmethod
    def favoritetagname_get(uid=''):
        """
        :return: 获取当前用户喜爱视频标签的SQL
        """
        SQL = """SELECT tag_name FROM {videotag_tbn} WHERE tag_id in (SELECT tagid FROM {usertag_tbn} WHERE uid={u_id})""".\
            format(videotag_tbn=config.VIDEO_TAG_TABLE_BASE_NAME, usertag_tbn=config.USER_VIDEO_TAG_TABLE_BASE_NAME, u_id=uid)
        return SQL

    @staticmethod
    def relation_insert(masterid, fanid):
        """
        :param masterid: 被关注人id
        :param fanid: 关注者id
        :return: 插入关注数据
        """
        SQL = """INSERT INTO {tbn} SET master_uid={muid}, fans_uid={fuid}""".format(tbn=config.USER_RELATION_TABLE_BASE_NAME,\
                                                muid=masterid, fuid=fanid)
        return SQL

    @staticmethod
    def relation_get(masterid, fanid):
        """
        :param masterid: 被关注人id
        :param fanid: 关注者id
        :return: 查找relation数据的sql
        """
        SQL = """SELECT {userrelation_fields} FROM {tbn} WHERE fans_uid={fuid} AND master_uid={muid}""".format(
            userrelation_fields=','.join(SQL_refector.UserRelation_fields), tbn=config.USER_RELATION_TABLE_BASE_NAME,\
            fuid=fanid, muid=masterid)
        return SQL

    @staticmethod
    def relations_master_get(uid, page=0):
        """
        :param uid: 当前用户id
        :return: 获取当前用户关注的所有人
        """
        # TODO 缺乏利用索引大小的优化
        SQL = """SELECT {userrelation_fields} FROM {tbn} WHERE fans_uid={fuid} LIMIT {limitbound} , {limitnum}""".format(
            userrelation_fields=','.join(SQL_refector.UserRelation_fields), tbn=config.USER_RELATION_TABLE_BASE_NAME,\
            fuid=uid, limitbound=config.USER_RELATION_PERPAGE*page, limitnum=config.USER_RELATION_PERPAGE)
        return SQL

    @staticmethod
    def relations_fan_get(uid, page=0):
        """
        :param uid: 当前用户id
        :return: 获取当前用户的所有粉丝
        """
        # TODO 缺乏利用索引大小的优化
        SQL = """SELECT {userrelation_fields} FROM {tbn} WHERE master_uid={muid} LIMIT {limitbound} , {limitnum}""".format(
            userrelation_fields=','.join(SQL_refector.UserRelation_fields), tbn=config.USER_RELATION_TABLE_BASE_NAME, \
            muid=uid, limitbound=config.USER_RELATION_PERPAGE*page, limitnum=config.USER_RELATION_PERPAGE)
        return SQL

    @staticmethod
    def relation_delete(masterid, fanid):
        """
        :param masterid:被关注者id
        :param fanid: 关注者id
        :return: 取消关注某人的SQL
        """
        SQL = """DELETE FROM {tbn} WHERE master_uid={muid} AND fans_uid={fuid}""".format(tbn=config.USER_RELATION_TABLE_BASE_NAME,\
                                                    muid=masterid, fuid=fanid)
        return SQL

    @staticmethod
    def videocomment_insert(vid, uid, comment, nickname, phtoturl, ref_comment_id=None):
        """
        :return:  插入评论的SQL
        """
        #comment是unicode
        if not ref_comment_id:
            SQL = """INSERT INTO {tbn} SET vid=\"{v_id}\", uid=\"{u_id}\", comment=\"{_comment}\" ,user_nickname=\"{_nickname}\", user_photo_url=\"{_photo}\"""".decode('utf8').format(tbn=config.VIDEO_COMMENT_TABLE_BASE_NAME,\
                                                 v_id=vid, u_id=uid, _comment=comment, _nickname=nickname, _photo=phtoturl)
        else:
            SQL = """INSERT INTO {tbn} SET vid=\"{v_id}\", uid=\"{u_id}\", comment=\"{_comment}\", ref_comment_id = {refid}, user_nickname=\"{_nickname}\", user_photo_url=\"{_photo}\"""".decode('utf8').format(tbn=config.VIDEO_COMMENT_TABLE_BASE_NAME,\
                                                 v_id=vid, u_id=uid, _comment=comment, refid=ref_comment_id, _nickname=nickname, _photo=phtoturl)
        return SQL

    @staticmethod
    def videocomments_get(vid):
        """
        :param vid:视频id
        :return: 获取某条视频的所有评论，根据点赞数排序
        """
        # TODO 根据状态筛选评论
        SQL = """SELECT {commentfields} FROM {tbn} WHERE vid={v_id} ORDER BY comment_like DESC""".\
            format(commentfields=','.join(SQL_refector.VideoComment_fields), tbn=config.VIDEO_COMMENT_TABLE_BASE_NAME, v_id=vid)
        return SQL

    @staticmethod
    def videocomment_update(commentid, **kwargs):
        """
        :param comment_id: 评论的id
        :param kwargs: 需要更新的字段和数据
        :return: 修改某条评论的SQL
        """
        SQL = """UPDATE {tbn} SET """.format(tbn=config.VIDEO_COMMENT_TABLE_BASE_NAME)
        setvalue = []
        for key in SQL_refector.VideoComment_fields:
            if kwargs.get(key, None) in (None, 'None'):
                continue
            setvalue.append(key + '="{' + key + '}"')
        SQL = (SQL + ','.join(setvalue) + """ WHERE comment_id=\"{_comment_id}\"""".format(_comment_id=commentid)).decode('utf8').format(**kwargs)
        return SQL

    @staticmethod
    def videocomment_incr_like(comment_id, likeamount=0):
        likeamount = str(likeamount)
        SQL = """UPDATE {tbn} SET `like`=`like`+{_like} WHERE comment_id={_cid}""".format(
            _like=likeamount, _cid=comment_id, tbn=config.VIDEO_COMMENT_TABLE_BASE_NAME)
        return SQL

    @staticmethod
    def videocomment_delete(comment_id):
        """
        :param comment_id:
        :return: 删除id为comment_id的评论
        """
        SQL = """DELETE FROM {tbn} WHERE comment_id={_comment_id} """.format(tbn=config.VIDEO_COMMENT_TABLE_BASE_NAME, _comment_id=comment_id)
        return SQL

    @staticmethod
    def message_insert(senduid, reciveuid, text):
        """
        :param senduid:发送者id
        :param reciveuid: 接收者id
        :param text: 文本内容
        :return: 插入私信数据的SQL
        """
        SQL = """INSERT INTO {tbn} SET send_uid={send_uid}, recive_uid={recive_uid}, text={_text}""".format(\
            tbn=config.MESSAGE_TABLE_BASE_NAME, send_uid=senduid, recive_uid=reciveuid, _text=text)
        return SQL

    @staticmethod
    def message_update(message_id, **kwargs):
        """
        :param message_id: message数据的id
        :param kwargs: 需要更新的字段和数据
        :return:更新message数据的SQL
        """
        SQL = """UPDATE {tbn} SET """.format(tbn=config.MESSAGE_TABLE_BASE_NAME)
        setvalue = []
        for key in SQL_refector.Message_fields:
            if kwargs.get(key, None) is None:
                continue
            setvalue.append(key + '={' + key + '}')
        SQL = (SQL + ','.join(setvalue) + """ WHERE message_id=\"{messageid}\"""".format(message_id=message_id)).decode('utf8').format(**kwargs)
        return SQL

    @staticmethod
    def messages_get_selfsend(uid, page=0):
        """
        :param uid: 用户id
        :return: 获取uid用户发送的所有私信
        """
        # TODO 根据状态筛选私信
        SQL = """SELECT {messagefields} FROM {tbn} WHERE send_uid={send_uid} LIMIT {limitbound} , {limitnum}""". \
            format(messagefields=','.join(SQL_refector.Message_fields), tbn=config.MESSAGE_TABLE_BASE_NAME,
                   send_uid=uid, limitbound=config.MESSAGE_PERPAGE*page, limitnum=config.MESSAGE_PERPAGE)
        return SQL

    @staticmethod
    def message_get_selfrecive(uid, page=0):
        """
        :param uid: 用户id
        :return: 获取uid用户接受的所有私信
        """
        # TODO 根据状态筛选私信
        SQL = """SELECT {messagefields} FROM {tbn} WHERE recive_uid={recive_uid} LIMIT {limitbound} , {limitnum}""". \
            format(messagefields=','.join(SQL_refector.Message_fields), tbn=config.MESSAGE_TABLE_BASE_NAME,
                   recive_uid=uid, limitbound=config.MESSAGE_PERPAGE*page, limitnum=config.MESSAGE_PERPAGE)
        return SQL

    @staticmethod
    def message_getnum_unread(uid):
        """
        :param uid: 用户id
        :return: 获取uid用户未读私信的数量
        """
        # TODO 根据状态筛选私信
        SQL = """SELECT COUNT(*)FROM {tbn} WHERE recive_uid={recive_uid} AND isread=0""". \
            format(tbn=config.MESSAGE_TABLE_BASE_NAME, recive_uid=uid)
        return SQL


    @staticmethod
    def message_delete(messageid):
        """
        :param message_id: 私信的id
        :return: 删除id为message_id的私信
        """
        SQL = """DELETE FROM {tbn} WHERE message_id={message_id} """.format(tbn=config.MESSAGE_TABLE_BASE_NAME,
                                                                            message_id=messageid)
        return SQL


# class Field(object):
#     def __init__(self, fields):
#         if isinstance(fields, (list, tuple)):
#             self.field = {}
#             for field in fields:
#                 n, t, nu, k, d, e = field
#                 self.field[n] = {}
#                 self.field[n]['field'] = n
#                 self.field[n]['type'] = t
#                 self.field[n]['null'] = nu
#                 self.field[n]['key'] = k
#                 self.field[n]['default'] = d
#                 self.field[n]['extra'] = e
#         if isinstance(fields, (str, unicode)):
#             self.field = fields
#
#     def get_field_list(self):
#         if isinstance(self.field, dict):
#             return self.field.keys()
#         return []
#
#     def __getattr__(self, key):
#         return self.field.get(key, None)
#
#     def __str__(self):
#         if isinstance(self.field, dict):
#             return '`{0}`'.format('`, `'.join(self.field.keys()))
#
#         if isinstance(self.field, (str, unicode)):
#             return self.field
#
#
# class DatabaseOp(object):
#     """ 操作MySQL """
#     def __init__(self, pool):
#         self.commit = False
#         self.pool = pool
#         self.cursor = pool.get_cursor()
#         self.logger = utils.get_logger(pool.config)
#
#     @gen.coroutine
#     def insert(self, fields, values):
#         """ 插入操作,返回id """
#         if len(fields) != len(values):
#             raise Exception, "fields and values's length not same"
#         sql = "INSERT INTO %s" % self.table
#         sql += "(`%s`)" % '`,`'.join(fields)
#         sv = len(fields) * "%s,"
#         sv = sv.strip(',')
#         sql += " VALUES(%s)" % sv
#         self.commit = True
#         try:
#             yield self.logger.debug(u'query mysql : {0}'.format(sql % tuple(values)))
#             yield self.cursor.execute(sql, values)
#             raise gen.Return(self.cursor.lastrowid)
#         except:
#             yield self.pool.rollback()
#
#     @gen.coroutine
#     def count(self, where = None):
#         """ 统计 """
#         sql = 'select count(*) from ' + self.table
#         if where:
#             sql += ' where ' + where
#         yield self.logger.debug(sql)
#         yield self.cursor.execute(sql)
#         r = self.cursor.fetchall()
#         raise gen.Return(r[0][0] if len(r) == 1 else 0)
#
#     @gen.coroutine
#     def max(self, field):
#         sql = 'select max(`{0}`) from ' + self.table
#         yield self.cursor.execute(sql)
#         r = self.cursor.fetchall()
#         raise gen.Return(r[0][0] if len(r) == 1 else 0)
#
#     @gen.coroutine
#     def select_one(self, fields = None, order = None, where = None):
#         r = yield self.select(fields, 1, order, where)
#         raise gen.Return(r[0] if len(r) == 1 else {})
#
#     @gen.coroutine
#     def select(self, fields=None, limit = None,
#                order = None, where = None):
#         """ 查询操作 """
#         if not fields:
#             fields = self.fields.get_field_list()   # 供后面格式化结果使用
#             sf = str(self.fields)                   # 创建sql语句使用
#         else:
#             sf = '`{0}`'.format('`,`'.join(fields))
#         sql = 'select {0} from `{1}` '.format(sf, self.table)
#         if where:
#             sql += 'where {0}'.format(where)
#         if order and isinstance(order, (dict, tuple)):
#             if isinstance(order, dict):
#                 order = order.items()[0]
#             orderby = ' DESC' if order[1] == -1 else 'ESC'
#             sql += ' order by `{0}` {1} '.format(order[0], orderby)
#         if limit:
#             if isinstance(limit, int):
#                 sql += ' limit {0} '.format(limit)
#             elif isinstance(limit, (tuple, list)):
#                 sql += ' limit {0}, {1} '.format(*limit)
#         yield self.logger.debug('query mysql : {0}'.format(sql))
#         yield self.cursor.execute(sql)
#         tmp = self.cursor.fetchall()
#         result = self.get_dict_result(tmp, fields)
#         raise gen.Return(result)
#
#     @gen.coroutine
#     def update(self, set_dict, where):
#         """ 更新操作, 返回id """
#         if not isinstance(set_dict, dict) and isinstance(where, dict): return
#         sql = 'update {0} set '.format(self.table) + self._format_set(set_dict)
#         sql += ' where ' + where
#         try:
#             yield self.logger.debug('query mysql : {0}'.format(sql))
#             self.commit = True
#             yield self.cursor.execute(sql)
#             raise gen.Return(self.cursor.lastrowid)
#         except:
#             yield self.pool.rollback()
#
#     @gen.coroutine
#     def remove(self, where = None):
#         """ where 为None则清空表 """
#         sql = 'delete from {0}'.format(self.table)
#         if where:
#             sql += ' where ' + where
#         self.commit = True
#         try:
#             yield self.logger.debug('query mysql : {0}'.format(sql))
#             result = yield self.cursor.execute(sql)
#             raise gen.Return(result)
#         except:
#             yield self.pool.rollback()
#
#     @gen.coroutine
#     def execute(self, sql, commit = False, *args, **kwargs):
#         yield self.cursor.execute(sql, *args, **kwargs)
#         self.commit = commit
#         raise gen.Return(self.cursor)
#
#     def _format_set(self, set_dict):
#         result = ''
#         for k, v in set_dict.items():
#             result += "`{0}`='{1}',".format(k, self.escape(v))
#         result = result.rstrip(',')
#         return result
#
#     def get_dict_result(self, lst, fields):
#         result = []
#         for l in lst:
#             tmp = dict(((key, l[i]) for i, key in enumerate(fields)))
#             result.append(tmp)
#         return result

