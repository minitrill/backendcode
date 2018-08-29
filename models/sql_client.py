#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/16 19:31
# @Author  : 曾凌峰
# @Site    : 
# @File    : sql_client.py
# @Software: PyCharm

import tormysql
import utils
import traceback
import sys

from tornado import gen
from tormysql import DictCursor

class SQLClient(object):
    __metaclass__ = utils.Singleton
    def __init__(self, config):
        # """
        # :param app: Tornado Application
        # """
        # if not app:
        #     raise ValueError('Tornado Application should not be None')
        # if not hasattr(app, 'config'):
        #     raise ValueError('Tornado Application should has "config" attr')
        # self._app = app
        # self._config = app.config
        self._config = config
        self._logger = utils.get_logger(self._config.DEBUG, self._config.MYSQL_LOGGER, self._config.TORMYSQL_LOG)
        self._pool = tormysql.ConnectionPool(
            max_connections = self._config.MAX_CONNECTION,
            idle_seconds = self._config.IDLE_SECONDS,
            wait_connection_timeout = self._config.WAIT_TIMEOUT_SECONDS,
            host = self._config.TORMYSQL_HOST,
            user = self._config.TORMYSQL_USER,
            passwd = self._config.TORMYSQL_PASSWORD,
            db = self._config.TORMYSQL_DB,
            charset = self._config.DEFAULTCHARSET,
        )

    @property
    def pool(self):
        return self._pool

    @property
    def logger(self):
        return self._logger

    @gen.coroutine
    def query_one(self, sql, args=None):
        data = None
        with (yield self.pool.Connection()) as conn:
            try:
                with conn.cursor(cursor_cls=DictCursor) as cursor:
                    yield cursor.execute(sql, args)
                    data = cursor.fetchone()
            except Exception, e:
                self.logger.error(traceback.print_exc())
                self.logger.error("Query error: %s", e.args)
            else:
                yield conn.commit()
        raise gen.Return(data)

    @gen.coroutine
    def query_all(self, sql, args=None):
        datas=None
        with (yield self.pool.Connection()) as conn:
            try:
                with conn.cursor(cursor_cls=DictCursor) as cursor:
                    yield cursor.execute(sql, args)
                    datas = cursor.fetchall()
            except Exception, e:
                self.logger.error(traceback.print_exc())
                self.logger.error("Query error: %s", e.args)
            else:
                yield conn.commit()
        raise gen.Return(datas)

    @gen.coroutine
    def execute(self, sql, args=None):
        ret = None
        with (yield self.pool.Connection()) as conn:
            try:
                with conn.cursor(cursor_cls=DictCursor) as cursor:
                    ret = yield cursor.execute(sql, args)
            except Exception, e:
                self.logger.error(traceback.print_exc())
                self.logger.error("Query error: %s", e.args)
                self.logger.error(sql)
                yield conn.rollback()
            else:
                yield conn.commit()
        raise gen.Return(ret)

    @gen.coroutine
    def execute_many(self, sql, args=None):
        with (yield self.pool.Connection()) as conn:
            try:
                with conn.cursor(cursor_cls=DictCursor) as cursor:
                    ret = yield cursor.execute(sql, args)
            except Exception, e:
                self.logger.error(traceback.print_exc())
                self.logger.error("Query error: %s", e.args)
                self.logger.error(sql)
                yield conn.rollback()
            else:
                yield conn.commit()
        raise gen.Return(ret)

    @gen.coroutine
    def execute_many_no_result(self, sqls=[]):
        with (yield self.pool.Connection()) as conn:
            try:
                with conn.cursor(cursor_cls=DictCursor) as cursor:
                    for sql in sqls:
                        yield cursor.execute(sql)
            except Exception, e:
                self.logger.error(traceback.print_exc())
                self.logger.error("Query error: %s", e.args)
                self.logger.error(sqls)
                yield conn.rollback()
            else:
                yield conn.commit()
        raise gen.Return(len(sqls))

    def db(self):
        return DataBase(self._pool, self._logger, self._config).db_connect()


class DataBase(object):
    def __init__(self, pool, logger, config):
        self._config = config
        self._pool = pool
        self._logger = logger

    @property
    def config(self):
        return self._config

    @property
    def pool(self):
        return self._pool

    @property
    def logger(self):
        return self._logger

    #@gen.coroutine
    def __enter__(self):
        # yield self.db_connect()
        # raise gen.Return(self)
        return self

    # @gen.coroutine
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db_close()
        # 异常的 type、value 和 traceback
        if exc_val and not isinstance(exc_val, gen.Return):
            traceback.print_exception(exc_type, exc_val, exc_tb)
            if isinstance(exc_val.message, unicode):
                self.logger.error("DB Context Error:" + exc_val.message.encode('utf8')+str(exc_tb))
            else:
                self.logger.error("DB Context Error:" + str(exc_val) + ":" + str(exc_tb))
            return False

    @gen.coroutine
    def db_connect(self):
        """连接数据库"""
        try:
            self.conn = yield self.pool.Connection()
        except Exception as e:
            yield self.logger.error('Connect Error:' + str(e))
        self.cursor = self.conn.cursor()
        self.SSCursor = self.conn.cursor(tormysql.SSCursor)
        if not self.cursor:
            raise (NameError, "Connect Failure")
        yield self.logger.warning("MySQL Database(" + str(self.config.TORMYSQL_HOST) + ") Connect Success")
        raise gen.Return(self)

    @gen.coroutine
    def db_close(self):
        """关闭数据库"""
        try:
            self.cursor.close()
            self.SSCursor.close()
            self.conn.close()
            yield self.logger.warning("MySQL Database(" + str(self.config.TORMYSQL_HOST) + ") Close")
        except Exception as e:
            yield self.logger.error("Close Error:" + str(e))

    @gen.coroutine
    def db_commit(self):
        """提交事务"""
        try:
            yield self.conn.commit()
            yield self.logger.warning("MySQL Database(" + str(self.config.TORMYSQL_HOST) + ") Commit")
        except Exception as e:
            yield self.logger.error("Commit Error:" + str(e))

    @gen.coroutine
    def execute_sql_value(self, sql, value):
        """
        执行带values集的sql语句
        :param sql: sql语句
        :param value: 结果值
        """
        try:
            yield self.cursor.execute(sql, value)
            yield self.db_commit()
        except Exception, e:
            if e.args[0] == 2013 or e.args[0] == 2006:  # 数据库连接出错，重连
                yield self.db_close()
                yield self.db_connect()
                yield self.db_commit()
                yield self.logger.error("execute |sql(value) - time out,reconnect")
                yield self.cursor.execute(sql, value)
            else:
                yield self.logger.error("execute |sql(value) - Error:" + str(e))
                yield self.logger.error("SQL : " + sql)
                yield self.conn.rollback()

    @gen.coroutine
    def execute_no_result(self, sql):
        """
        执行SQL语句,不获取查询结果,而获取执行语句的结果
        :param sql: SQL语句
        """
        effect_row=0
        try:
            effect_row = yield self.cursor.execute(sql)
            yield self.db_commit()
        except Exception, e:
            if e.args[0] == 2013 or e.args[0] == 2006:  # 数据库连接出错，重连
                yield self.db_close()
                yield self.db_connect()
                yield self.logger.error("execute |sql(no result) - time out,reconnect")
                effect_row = yield self.cursor.execute(sql)
                yield self.db_commit()
            else:
                yield self.logger.error("execute |sql(no result) - Error:" + str(e))
                yield self.logger.error("SQL : " + sql)
                yield self.conn.rollback()
        raise gen.Return(effect_row)

    @gen.coroutine
    def execute(self, sql):
        """
        执行SQL语句
        :param sql: SQL语句
        :return: 获取SQL执行并取回的结果
        """
        res = ()
        try:
            yield self.cursor.execute(sql)
            res = self.cursor.fetchall()
        except Exception, e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            if e.args[0] == 2013 or e.args[0] == 2006:  # 数据库连接出错，重连
                yield self.db_close()
                yield self.db_connect()
                yield self.db_commit()
                yield self.logger.error("execute |sql - time out,reconnect")
                yield self.logger.error("execute |sql - Error 2006/2013 :" + str(e))
                yield self.logger.error("sql = " + str(sql))
                res = yield self.execute(sql)  # 重新执行
            else:
                yield self.logger.error("execute |sql - Error:" + str(e))
                yield self.logger.error('SQL : ' + sql)
                yield self.conn.rollback()
        raise gen.Return(res)

    def execute_Iterator(self, sql, pretchNum=1000):
        """
        执行SQL语句(转化为迭代器)
        :param sql: SQL语句
        :param pretchNum: 每次迭代数目
        :return: 迭代器
        """
        yield self.logger.info('执行:' + sql)
        __iterator_count = 0
        __result = None
        __result_list = []
        try:
            Resultnum = self.cursor.execute(sql)
            for i in range(Resultnum):
                __result = self.cursor.fetchone()
                __result_list.append(__result)
                __iterator_count += 1
                if __iterator_count == pretchNum:
                    yield __result_list
                    __result_list = []
                    __iterator_count = 0
            yield __result_list  # 最后一次返回数据
        except Exception, e:
            yield self.logger.error('execute_Iterator error:' + str(e))
            yield self.logger.error('SQL : ' + sql)

    @gen.coroutine
    def execute_many(self, sql, params):
        """
        批量执行SQL语句
        :param sql: sql语句(含有%s)
        :param params: 对应的参数列表[(参数1,参数2..参数n)(参数1,参数2..参数n)...(参数1,参数2..参数n)]
        :return: affected_rows
        """
        affected_rows = 0
        try:
            yield self.cursor.executemany(sql, params)
            affected_rows = self.cursor.rowcount
            yield self.db_commit()
        except Exception, e:
            if e.args[0] == 2013 or e.args[0] == 2006:  # 数据库连接出错，重连
                yield self.db_close()
                yield self.db_connect()
                yield self.db_commit()
                yield self.logger.error("execute |sql - time out,reconnect")
                yield self.logger.error("execute |sql - Error 2006/2013 :" + str(e))
                yield self.logger.error("sql = " + str(sql))
                yield self.execute_many(sql, params)  # 重新执行
            else:
                yield self.logger.error("execute many|sql - Error:" + str(e))
                yield self.logger.error('SQL : ' + sql)
                yield self.conn.rollback()
                raise gen.Return(-1)
        raise gen.Return(affected_rows)

    @gen.coroutine
    def execute_many_no_result(self, sqls=[]):
        """
        批量执行SQL语句
        :param sql: sql语句集合
        :return: 无
        """
        try:
            for sql in sqls:
                yield self.cursor.execute(sql)
            yield self.db_commit()
        except Exception, e:
            if e.args[0] == 2013 or e.args[0] == 2006:  # 数据库连接出错，重连
                yield self.db_close()
                yield self.db_connect()
                yield self.db_commit()
                yield self.logger.error("execute |sql - time out,reconnect")
                yield self.logger.error("execute |sql - Error 2006/2013 :" + str(e))
                yield self.logger.error("sql = " + str(sql))
                yield self.execute_many_no_result(sqls)  # 重新执行
            else:
                yield self.logger.error("execute many|sql - Error:" + str(e))
                yield self.logger.error('SQL : ' + sql)
                yield self.conn.rollback()


    @gen.coroutine
    def execute_SScursor(self, sql):
        """使用MySQLdb SSCursor类实现逐条取回
        请不要使用此方法来进行增、删、改操作()
        最好在with[上下文管理器内使用]"""
        # sql不要带 ';'
        # 有可能会发生 2014, "Commands out of sync; you can't run this command now"
        # 详见 [MySQL-python: Commands out of sync](https://blog.xupeng.me/2012/03/13/mysql-python-commands-out-of-sync/)
        sql = sql.strip(';')
        # 只能执行单行语句
        if len(sql.split(';')) >= 2:
            raise gen.Return([])
        try:
            yield self.SSCursor.execute(sql)
            raise gen.Return(self.SSCursor)
        except Exception, e:
            yield self.logger.error("execute SScursor |sql - Error:" + str(e))
            yield self.logger.error('SQL : ' + sql)
            yield self.conn.rollback()
            raise gen.Return([])



if __name__ == '__main__':
    from config import config
    from tornado.ioloop import IOLoop

    @gen.coroutine
    def test():
        with (yield DataBase(config['development']).db_connect()) as db:
            sqlstr = 'select * from User_1'
            queryresult = yield db.execute(sqlstr)
            print queryresult

    ioloop = IOLoop.instance()
    ioloop.run_sync(test)