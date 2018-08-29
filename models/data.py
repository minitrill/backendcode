#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/16 19:31
# @Author  : 曾凌峰
# @Site    : 
# @File    : data.py
# @Software: PyCharm

import utils
import errors
import re
import os
import mzgeohash

from tornado import gen
from models import SQL_refector
from config import static

class Data(object):
    """MySQL和Redis 数据获取"""
    __metaclass__ = utils.Singleton

    def __init__(self, db, cache, remote):
        if not db:
            raise RuntimeError('db should not be None')
        self.db = db
        if cache:
            self.cache = cache
        if remote:
            self.remote = remote

    def generate_password_hash(self, password):
        pass

    def verify_password(self, password):
        pass

    #创建用户
    @gen.coroutine
    def create_user(self, **json):
        # with (yield self.db.db()) as db:
        Rules.rule_usercreate(**json)
        account = json['account']
        #账户查重
        cnk_SQL = SQL_refector.user_get(account)
        cnk_res = yield self.db.query_one(cnk_SQL)
        if cnk_res:
            raise RuntimeError(errors.ACCOUNT_ALREADY_EXIST)
        account_hash = static.get_hash(account)
        table_num = str(static.get_table_num(account_hash))
        json['uid'] = account_hash
        json['tbn'] = static.USER_TABLE_BASE_NAME+'_'+str(table_num)
        #头像处理
        portrait_base64=json.get('portrait', None)
        if portrait_base64:
            path = os.path.join(static.config.PORTRAIT_PATH, table_num)
            filename = str(account_hash)+'.png'
            photopathname = utils.load_picture(path, filename, portrait_base64)
            photourl = utils.path_to_url(static.config.DATA_PATH, photopathname)
            json['photo_url'] = photourl
        #为birth添加默认值
        if len(json.get('birth', '')) < 3:
            json['birth']='1900-01-01'
            json['age'] = '0'
        SQL = SQL_refector.user_insert(**json)
        effect_row = yield self.db.execute(SQL)
        nickname = json.get('nickname', None)
        uid = json.get('uid', None)
        account = json.get('account', None)
        raise gen.Return((uid, nickname, account))

    #检查登陆数据
    @gen.coroutine
    def check_user(self, **json):
        #with (yield self.db.db()) as db:
        account, password = Rules.rule_userlogin(**json)
        getuser_SQL = SQL_refector.user_get(account)
        getuser_res = yield self.db.query_one(getuser_SQL)
        if getuser_res.get('status', 0) < 0:
            raise RuntimeError(errors.ACCOUNT_BAN)
        if not getuser_res:
            raise RuntimeError(errors.ACCOUNT_PASSWORD_ERROR)
        if not password == getuser_res['password']:
            raise RuntimeError(errors.ACCOUNT_PASSWORD_ERROR)
        '''
        getuser_res参考数据
        ((-840729673, 0, u'\u5f20\u4e09123', u'/data/minitrill/user/photo/default/default.jpg', u'lemon123', u'aa1321231', u'\u4fdd\u5bc6', 18, None, u'\u4fdd\u5bc6', u'\u4e2d\u56fd', u'\u4fdd\u5bc6', u'\u4fdd\u5bc6', 0, 0, datetime.datetime(2018, 7, 19, 15, 37, 40)),)
        '''
        nickname = getuser_res['nickname']
        uid = getuser_res['uid']
        account = getuser_res['account']
        raise gen.Return((uid, nickname, account))

    #获取用户数据
    @gen.coroutine
    def get_user(self, uid):
        data = self.cache.getuser(uid)
        if not data:
            getuser_SQL = SQL_refector.user_getwithid(uid)
            data = yield self.db.query_one(getuser_SQL)
        if not data:
            raise gen.Return({})
        else:
            self.cache.setuser(uid, **data)
            raise gen.Return([Jsonify.userjson(data)])

    #修改用户数据
    @gen.coroutine
    def update_user(self, uid, **json):
        updateuser_SQL = SQL_refector.user_update(uid, **json)
        effect_row = yield self.db.execute(updateuser_SQL)
        if self.cache.getuser(uid):
            self.cache.deleteuser(uid)

    #获取视频标签
    @gen.coroutine
    def get_videotag(self):
        #with (yield self.db.db()) as db:
        videotag_SQL = SQL_refector.videotag_get()
        videotag_res = yield self.db.query_all(videotag_SQL)
        raise gen.Return([videotag_record['tag_name'] for videotag_record in videotag_res])

    #设置喜爱的视频标签
    @gen.coroutine
    def insert_favoritetag(self, user, **json):
        if not user:
            raise RuntimeError(errors.LOGIN_COOKIES_INVALID)
        if not json.get('tags', None):
            raise RuntimeError(errors.JSON_SHOULD_BE_NOT_NONE)
        #with (yield self.db.db()) as db:
        favoritetag_SQL = SQL_refector.favoritetag_get(uid=user.uid)
        favoritetag_res = yield self.db.query_all(favoritetag_SQL)
        if favoritetag_res:
            raise RuntimeError(errors.API_PERMISSION_DENY)
        favoritetaginsert_SQLS=[]
        for tag in json.get('tags'):
            favoritetaginsert_SQL = SQL_refector.favoritetag_insert(user.uid, tag)
            favoritetaginsert_SQLS.append(favoritetaginsert_SQL)
        yield self.db.execute_many_no_result(favoritetaginsert_SQLS)

    #获取喜爱的视频标签名称
    @gen.coroutine
    def get_favoritetagname(self, user):
        if not user:
            raise RuntimeError(errors.LOGIN_COOKIES_INVALID)
        #with (yield self.db.db()) as db:
        videotag_SQL = SQL_refector.favoritetagname_get(uid=user.uid)
        videotag_res = yield self.db.query_all(videotag_SQL)
        raise gen.Return([videotag_record['tag_name'] for videotag_record in videotag_res])

    #获取所有视频
    @gen.coroutine
    def get_videos(self, page):
        #with (yield self.db.db()) as db:
        getvideos_SQL = SQL_refector.videos_get(page)
        getvideos_res = yield self.db.query_all(getvideos_SQL)
        if not getvideos_res:
            raise gen.Return([])
        else:
            datas = []
            for data in getvideos_res:
                datas.append(Jsonify.videojson(data))
            #为所有的视频观看次数+1
            # TODO 这个间隙可能会导致数据出问题，多个请求到来会导致丢失一些记录
            sqls=[]
            for video in datas:
                vid = video.get('vid', None)
                view = video.get('view', None)
                if vid is not None:
                    updatevideo_SQL = SQL_refector.video_incr_share_view_like(vid, viewamount=1)
                    sqls.append(updatevideo_SQL)
            yield self.db.execute_many_no_result(sqls)
            raise gen.Return(datas)

    #获取某个视频
    @gen.coroutine
    def get_video(self, video_id):
        getvideo_res = self.cache.getvideo(video_id)
        if not getvideo_res:
            getvideo_SQL = SQL_refector.video_get(video_id)
            getvideo_res = yield self.db.query_one(getvideo_SQL)
        if not getvideo_res:
            raise gen.Return([])
        else:
            self.cache.setvideo(video_id, **getvideo_res)
            raise gen.Return([Jsonify.videojson(getvideo_res)])

    @gen.coroutine
    def get_videoswithvids(self, vids):
        getvideos_res = []
        for vid in vids:
            video = yield self.get_video(vid)
            getvideos_res.extend(video)
        if not getvideos_res:
            getvideos_SQL = SQL_refector.videos_getwithvids(vids)
            getvideos_res = yield self.db.query_all(getvideos_SQL)
        if not getvideos_res:
            raise gen.Return([])
        else:
            datas = []
            for data in getvideos_res:
                datas.append(Jsonify.videojson(data))
            raise gen.Return(datas)

    #获取某个用户的视频
    @gen.coroutine
    def get_videos_uid(self, uid, page):
        getvideo_SQL = SQL_refector.videos_getwithuid(uid, page)
        getvideo_res = yield self.db.query_all(getvideo_SQL)
        if not getvideo_res:
            raise gen.Return([])
        else:
            datas = []
            for data in getvideo_res:
                datas.append(Jsonify.videojson(data))
            raise gen.Return(datas)

    #获取附近的视频
    @gen.coroutine
    def get_videoswithneighbour(self, longitude, latitude, level, page):
        if not Rules.rule_geo(latitude=latitude, longitude=longitude, level=level):
            raise RuntimeError(errors.GEOINFORMATION_ERROR)
        longitude=round(float(longitude), 10)
        latitude=round(float(latitude), 10)
        level = int(level)
        geohash = mzgeohash.encode((longitude, latitude), level)
        neighbours = mzgeohash.neighbors(geohash).values()
        getvideos_SQL = SQL_refector.videos_getwithgeo(neighbours, level, page)
        getvideos_res = yield self.db.query_all(getvideos_SQL)
        if not getvideos_res:
            raise gen.Return([])
        else:
            datas = []
            for data in getvideos_res:
                datas.append(Jsonify.videojson(data))
            raise gen.Return(datas)

    #给视频分享+1
    @gen.coroutine
    def share_video(self, vid):
        if not self.cache.sharevideo(vid):
            updatevideo_SQL = SQL_refector.video_incr_share_view_like(vid, shareamount=1)
            effect_row = yield self.db.execute(updatevideo_SQL)

    @gen.coroutine
    def view_video(self, vid):
        if not self.cache.viewvideo(vid):
            updatevideo_SQL = SQL_refector.video_incr_share_view_like(vid, viewamount=1)
            effect_row = yield self.db.execute(updatevideo_SQL)

    #给视频点赞+1
    @gen.coroutine
    def like_video(self, vid):
        # with (yield self.db.db()) as db:
        #     getvideo_SQL = SQL_refector.video_get(vid)
        #     getvideo_res = yield db.execute(getvideo_SQL)
        #     if not getvideo_res:
        #         raise ValueError(errors.VIDEO_NOT_FOUND)
        #     like = int(getvideo_res[0][8])
        # TODO 这个间隙可能会导致数据出问题，多个点赞到来会导致丢失一些点赞的记录
        # TODO 可以用一条sql语句完成操作 `like`=`like`+'1'
        if not self.cache.likevideo(vid):
            updatevideo_SQL = SQL_refector.video_incr_share_view_like(vid, likeamount=1)
            effect_row = yield self.db.execute(updatevideo_SQL)

    #关注某人
    @gen.coroutine
    def focus_user(self, masterid, fanid):
        #with (yield self.db.db()) as db:
        masterid=int(masterid)
        fanid=int(fanid)
        insertrelation_SQL = SQL_refector.relation_insert(masterid, fanid)
        effect_row = yield self.db.execute(insertrelation_SQL)
        if not effect_row:
            raise gen.Return()
        # TODO 这个间隙可能会导致数据出问题，多个请求到来会导致丢失一些记录
        # yield self.update_user(masterid, fans='fans+1')
        # yield self.update_user(fanid, follow='follow+1')

        # TODO 可以用一条sql语句完成操作
        updateuser_SQL = SQL_refector.user_incr_follow_fan(masterid, fanamount=1)
        yield self.db.execute(updateuser_SQL)
        updateuser_SQL = SQL_refector.user_incr_follow_fan(fanid, followamount=1)
        yield self.db.execute(updateuser_SQL)

    #取消关注某人
    @gen.coroutine
    def defocus_user(self, masterid ,fanid):
        #with (yield self.db.db()) as db:
        masterid = int(masterid)
        fanid = int(fanid)
        deleterelation_SQL = SQL_refector.relation_delete(masterid, fanid)
        effect_row = yield self.db.execute(deleterelation_SQL)
        if not effect_row:
            raise gen.Return()
        # yield self.update_user(masterid, fans='fans-1')
        # yield self.update_user(fanid, follow='follow-1')
        # TODO 这个间隙可能会导致数据出问题，多个请求到来会导致丢失一些记录
        updateuser_SQL = SQL_refector.user_incr_follow_fan(masterid, fanamount=-1)
        yield self.db.execute(updateuser_SQL)
        updateuser_SQL = SQL_refector.user_incr_follow_fan(fanid, followamount=-1)
        yield self.db.execute(updateuser_SQL)

    #是否关注了某人
    @gen.coroutine
    def isfollow(self, masterid, fanid):
        #with (yield self.db.db()) as db:
        getrelaiton_SQL = SQL_refector.relation_get(masterid, fanid)
        getrelation_res = yield self.db.query_one(getrelaiton_SQL)
        if getrelation_res:
            raise gen.Return(True)
        else:
            raise gen.Return(False)

    #获取所有关注的数据
    @gen.coroutine
    def get_masteruser(self, selfid, page):
        getrelation_SQL = SQL_refector.relations_master_get(selfid, page)
        getrelation_res = yield self.db.query_all(getrelation_SQL)
        data = []
        for relation in getrelation_res:
            masterid=relation['master_uid']
            userdata = yield self.get_user(masterid)
            if userdata:
                data.append(userdata)
        raise gen.Return(data)

    #获取所有粉丝的数据
    @gen.coroutine
    def get_fanuser(self, selfid, page):
        #with (yield self.db.db()) as db:
        getrelation_SQL = SQL_refector.relations_fan_get(selfid, page)
        getrelation_res = yield self.db.query_all(getrelation_SQL)
        data = []
        for relation in getrelation_res:
            fanid=relation['fans_uid']
            userdata = yield self.get_user(fanid)
            if userdata:
                data.append(userdata)
        raise gen.Return(data)

    #插入视频评论
    @gen.coroutine
    def insert_videocomment(self, vid, uid, **json):
        #with (yield self.db.db()) as db:
        comment = Rules.getfromrequest(json, 'comment')
        ref_comment_id = json.get('ref_comment_id', None)
        user = yield self.get_user(uid)
        insertcomment_SQL = SQL_refector.videocomment_insert(vid, uid, comment, user.get('nickname', ''), user.get('photo_url', ''), ref_comment_id)
        effect_row = yield self.db.execute(insertcomment_SQL)


    #获取某个视频的所有评论
    @gen.coroutine
    def get_videocomment(self, vid):
        #with (yield self.db.db()) as db:
        getcomment_SQL = SQL_refector.videocomments_get(vid)
        getcomment_res = yield self.db.query_all(getcomment_SQL)
        if not getcomment_res:
            raise gen.Return([])
        else:
            datas = []
            for data in getcomment_res:
                datas.append(Jsonify.commentjson(data))
            raise gen.Return(datas)

    #点赞某条评论
    @gen.coroutine
    def update_like_videocomment(self, commentid):
        #with (yield self.db.db()) as db:
        updatecomment_SQL = SQL_refector.videocomment_incr_like(commentid, likeamount=1)
        effect_row = yield self.db.execute(updatecomment_SQL)

    #删除某条评论
    @gen.coroutine
    def delete_videocomment(self, commentid):
        #with (yield self.db.db()) as db:
        deletecomment_SQL = SQL_refector.videocomment_delete(commentid)
        effect_row = yield self.db.execute(deletecomment_SQL)

    #发送私信
    @gen.coroutine
    def insert_message(self, senduid, **json):
        #with (yield self.db.db()) as db:
        reciveuid, text = Rules.getfromrequest(json, 'recive_uid', 'text')
        insertmessage_SQL = SQL_refector.message_insert(senduid, reciveuid, text)
        effect_row = yield self.db.execute(insertmessage_SQL)

    #把私信标记为已读
    @gen.coroutine
    def read_message(self, messageid):
        #with (yield self.db.db()) as db:
        readmessage_SQL = SQL_refector.message_update(messageid, isread='\'1\'')
        effect_row = yield self.db.execute(readmessage_SQL)

    #获取收到的私信
    @gen.coroutine
    def get_recive_message(self, uid, page=0):
        #with (yield self.db.db()) as db:
        getmessages_SQL = SQL_refector.message_get_selfrecive(uid, page)
        getmessage_res = yield self.db.query_all(getmessages_SQL)
        if not getmessage_res:
            raise gen.Return(None)
        else:
            datas = []
            for data in getmessage_res:
                #特殊处理字段
                if data.get('send_time', None):
                    data['send_time'] = str(data['send_time'])
                datas.append(data)
            raise gen.Return(datas)

    #获取发送的私信
    @gen.coroutine
    def get_send_message(self, uid, page=0):
        #with (yield self.db.db()) as db:
            getmessages_SQL = SQL_refector.messages_get_selfsend(uid, page)
            getmessage_res = yield self.db.query_all(getmessages_SQL)
            if not getmessage_res:
                raise gen.Return(None)
            else:
                datas = []
                for data in getmessage_res:
                    #特殊处理字段
                    if data.get('send_time', None):
                        data['send_time'] = str(data['send_time'])
                    datas.append(data)
                raise gen.Return(datas)

    #删除私信
    @gen.coroutine
    def delete_message(self, messageid):
        #with (yield self.db.db()) as db:
        deletemessage_SQL = SQL_refector.message_delete(messageid)
        effect_row = yield self.db.execute_no_result(deletemessage_SQL)

    #未读私信
    @gen.coroutine
    def unread_messagenum(self, uid):
        #with (yield self.db.db()) as db:
        getmessagenum_SQL = SQL_refector.message_getnum_unread(uid)
        unreadnum = yield self.db.query_one(getmessagenum_SQL)
        raise gen.Return(unreadnum)


class Rules(object):
    """对数据的合法性检查"""
    @staticmethod
    def rule_usercreate(**json):
        #非空检查
        nickname, account, password = Rules.getfromrequest(json, 'nickname', 'account', 'password')
        #合法性检查
        if not Rules.rule_nickname(nickname):
            raise ValueError(errors.NAMING_RULE[u'nickname'])
        if not Rules.rule_account(account):
            raise ValueError(errors.NAMING_RULE[u'account'])
        if not Rules.rule_password(password):
            raise ValueError(errors.NAMING_RULE[u'password'])

    @staticmethod
    def rule_userlogin(**json):
        #非空检查
        account, password = Rules.getfromrequest(json, 'account', 'password')
        return account, password

    # 从json里获取一些必填的属性
    @staticmethod
    def getfromrequest(json, *options):
        args = []
        for arg in options:
            prop = json.pop(arg, None)
            if prop is None:
                raise ValueError(errors.NOT_NONE.get(arg, str(arg).decode('utf8')+u'不能为空'))
            args.append(prop)
        if len(args) > 1:
            return args
        else:
            return args[0]

    #检查地理信息
    @staticmethod
    def rule_geo(longitude, latitude, level):
        if not (isinstance(latitude, str) or isinstance(latitude, unicode)) or len(latitude) < 8:
            return False
        if not (isinstance(longitude, str) or isinstance(longitude, unicode)) or len(longitude) < 8:
            return False
        if int(level) < 0 or int(level) > 10:
            return False
        return True

    @staticmethod
    def rule_password(password):
        """
        :param password:
        :return: 密码合法性判断 数字字母组合，不小于8位
        """
        return Rules.checkContainNum(password) and (Rules.checkContainLower(password) \
            or Rules.checkContainUpper(password)) and Rules.checklen(password, 8)

    @staticmethod
    def rule_account(account):
        """
        :param account:
        :return: 账号合法性判断 大写或小写加数字组合，不允许其他符号，6位
        """
        return (not Rules.checkSymbol(account)) and Rules.checklen(account, 6)

    @staticmethod
    def rule_nickname(nickname):
        """
        :param nickname:
        :return: 昵称合法性判断 允许有相同的，长度不少于4位
        """
        # TODO 昵称敏感词检查接口
        return Rules.checklen(nickname, 4)

    @staticmethod
    def checklen(str, length):
        """
        :param str:
        :return: 长度检查
        """
        return len(str) >= length

    @staticmethod
    def checkContainUpper(str):
        """
        :param str:
        :return: 是否有大写字母
        """
        pattern = re.compile('[A-Z]+')
        match = pattern.findall(str)
        if match:
            return True
        else:
            return False

    @staticmethod
    def checkContainNum(str):
        """
        :param str:
        :return: 是否有数字
        """
        pattern = re.compile('[0-9]+')
        match = pattern.findall(str)
        if match:
            return True
        else:
            return False

    @staticmethod
    def checkContainLower(str):
        """
        :param str:
        :return: 是否有小写字母
        """
        pattern = re.compile('[a-z]+')
        match = pattern.findall(str)

        if match:
            return True
        else:
            return False

    @staticmethod
    def checkSymbol(str):
        """
        :param str:
        :return: 是否有符号
        """
        pattern = re.compile('([^a-z0-9A-Z])+')
        match = pattern.findall(str)
        if match:
            return True
        else:
            return False


class Jsonify(object):
    @staticmethod
    def videojson(videodict):
        if videodict.get('upload_time', None):
            videodict['upload_time'] = str(videodict['upload_time'])
        if videodict.get('latitude', None):
            videodict['latitude'] = str(videodict['latitude'])
        if videodict.get('longitude', None):
            videodict['longitude'] = str(videodict['longitude'])
        if videodict.get('vid', None):
            videodict['vid'] = str(videodict['vid'])
        if videodict.get('uploader_uid', None):
            videodict['uploader_uid'] = str(videodict['uploader_uid'])
        return videodict

    @staticmethod
    def userjson(userdict):
        if userdict.get('password', None):
            userdict['password']=''
        if userdict.get('uid', None):
            userdict['uid'] = str(userdict['uid'])
        if userdict.get('birth', None):
            userdict['birth'] = str(userdict['birth'])
        if userdict.get('register_date', None):
            userdict['register_date'] = str(userdict['register_date'])
        if userdict.get('uid', None):
            userdict['uid'] = str(userdict['uid'])
        return userdict

    @staticmethod
    def commentjson(commentdict):
        if commentdict.get('comment_time', None):
            commentdict['comment_time'] = str(commentdict['comment_time'])
        return commentdict
