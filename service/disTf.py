# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.split(os.path.realpath(__file__))[0]+"/..")
import tornado
from tornado.web import Application
from util.ApiConfiger import ApiConfig
from handlers.train_handler import TrainHandler
import logging

class DisDeepService(object):
    def __init__(self):
        self.config = ApiConfig()

    def start(self):
        app = tornado.web.Application([
            (r"/v1/train", TrainHandler)
            ])
        app.listen(self.config.getint("service", "port"))
        logging.info("service start ...")
        tornado.ioloop.IOLoop.current().start()

if __name__ == '__main__':
    service = DisDeepService()
    print 'start ....'
    service.start()
