# coding: utf-8
import tornado
import os
import json
import hashlib
from util.ApiConfiger import ApiConfig
from util.RedisHelper import RedisHelper
from util.MysqlHelper import MysqlHelper
from util.tool import need_auth
import logging
import traceback

class UserHandler(tornado.web.RequestHandler):
    def get(self):
        logging.info('GET stub')
        self.write("good")
        #self.finish()
        #self.write("good")

    def initUserHome(self, name):
        if os.path.exists('/mnt/'+name):
            return False
        os.mkdir('/mnt/'+name)
        return True

    @tornado.web.asynchronous
    def post(self, action = ""):
        try:
            print "action: " + action
            print self.request.body
            userInfo = json.loads(self.request.body)
            name = userInfo.get("name")
            passwd = userInfo.get("pass")
            digest = hashlib.md5(passwd.encode('utf-8')).hexdigest()
            sql = "insert into users (name, password) values ('{0}', '{1}')".format(name, digest)
            MysqlHelper().execute(sql)
            # TODO init user home
            if not self.initUserHome(name):
                self.write("user home already exists")
            else:
                self.write("ok")
        except:
            traceback.print_exc()
        finally:
            self.finish()

    @tornado.web.asynchronous
    def delete(self, action = ""):
        try:
            print "action: " + action
            print self.request.body
            self.write("ok")
        except:
            traceback.print_exc()
        finally:
            self.finish()
