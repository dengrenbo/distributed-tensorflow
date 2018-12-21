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
            print 'get auth head'
            print dir(headers)
            print headers
            authInfo = headers.get('Authorization', None)
            if authInfo is None or not authInfo.startswith('Basic '):
                return False
            print authInfo
            authDecoded = base64.decodestring(authInfo[6:])
            username, passwd = authDecoded.split(":")
            print username, passwd
            digestFromUser = hashlib.md5(passwd.encode('utf-8')).hexdigest()
            print "digest from user: " + digestFromUser
            sql = "select password from users where name = '{0}'".format(username)
            res = MysqlHelper().execute(sql, True)
            if not res:
                return False
            digestFromDb = res[0][0]
            print "digest from db: " + digestFromDb
            handler.basicUsername = username
            return digestFromUser == digestFromDb
        handler = None
        if len(args) > 0 and isinstance(args[0], tornado.web.RequestHandler):
            print 'yes, got handler cls'
            handler = args[0]
            print '\n'
            print '='*10
            print handler.request.headers
            print '='*10
            print '\n'
            if not verify_auth(handler.request.headers):
                print 'auth failed ...'
                set_error(handler)
                return False
        else:
            print 'no handler cls'
            return False
        print 'real func ......'
        return func(*args, **kwargs)
    return wrapper
