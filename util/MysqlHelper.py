# -*- coding: utf-8 -*-
import mysql.connector
import mysql.connector.pooling
import traceback
from ApiConfiger import ApiConfig

class MysqlHelper(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(MysqlHelper, cls).__new__(cls, *args, **kwargs)
        return cls.instance

    def __init__(self):
        conf = {
            'user': ApiConfig().get("mysql", "user"),
            'password': ApiConfig().get("mysql", "pass"),
            'host': ApiConfig().get("mysql", "host"),
            'port': ApiConfig().get("mysql", "port"),
            'database': ApiConfig().get("mysql", "db")
        }
        # self.cnx = mysql.connector.connect(**conf)
        self.cnxPool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mysql_pool",
                                                                   pool_size=ApiConfig().getint("mysql", "pool"),
                                                                   **conf)

    def execute(self, sql, fetch=False):
        '''
        :param sql:
        :return: [ (col-1, ...), ... ]
        '''
        try:
            '''
            cur = self.cnx.cursor()
            cur.execute(sql)
            return cur.fetchall() if fetch else None
            '''
            cnx = self.cnxPool.get_connection()
            cur = cnx.cursor()
            cur.execute(sql)
            return cur.fetchall() if fetch else None
        except:
            print 'mysql execute error'
            raise Exception(sql + "execute error: " + traceback.format_exc())
        finally:
            if cur:
                cur.close()
            if cnx:
                cnx.commit()
                cnx.close()

    def executeSql(self, sql, fetch=False):
        '''
        :param sql:
        :return: rowcount, [ (col-1, ...), ... ]
        '''
        try:
            cnx = self.cnxPool.get_connection()
            cur = cnx.cursor()
            cur.execute(sql)
            data = None
            if fetch:
                data = cur.fetchall()
            return cur.rowcount, data if fetch else None
        except:
            print 'mysql execute error'
            raise Exception(sql + "execute error: " + traceback.format_exc())
        finally:
            if cur:
                cur.close()
            if cnx:
                cnx.commit()
                cnx.close()

    def poolexecute(self):
        pass
