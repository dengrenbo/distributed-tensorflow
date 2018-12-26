# coding: utf-8
import tornado
import base64
from MysqlHelper import MysqlHelper
import hashlib

def need_auth(func):
    def wrapper(*args, **kwargs):
        def set_error(handler):
            handler.set_status(401)
            handler.set_header('WWW-Authenticate', 'Basic realm=Restricted')
            handler._transforms = []
            handler.finish()
        def verify_auth(headers):
            authInfo = headers.get('Authorization', None)
            if authInfo is None or not authInfo.startswith('Basic '):
                return False
            authDecoded = base64.decodestring(authInfo[6:])
            username, passwd = authDecoded.split(":")
            digestFromUser = hashlib.md5(passwd.encode('utf-8')).hexdigest()
            sql = "select password from users where name = '{0}'".format(username)
            res = MysqlHelper().execute(sql, True)
            if not res:
                return False
            digestFromDb = res[0][0]
            handler.basicUsername = username
            return digestFromUser == digestFromDb
        handler = None
        if len(args) > 0 and isinstance(args[0], tornado.web.RequestHandler):
            handler = args[0]
            if not verify_auth(handler.request.headers):
                set_error(handler)
                return False
        else:
            return False
        return func(*args, **kwargs)
    return wrapper
