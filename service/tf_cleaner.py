# coding: utf-8
from __future__ import print_function
import sys
import os
sys.path.append(os.path.split(os.path.realpath(__file__))[0]+"/..")
from util.RedisHelper import RedisHelper
from util.ApiConfiger import ApiConfig
import kubernetes
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
from multiprocessing import Pool
import time
import json
import importlib
import traceback


class Cleaner(object):
    def __init__(self):
        self.pool = Pool(processes=4)
        self.eventHandlers = []

    def loadHandlers(self):
        handlerStrs = ApiConfig().get("event", "handlers")
        handlerNames = handlerStrs.split(",")
        for name in handlerNames:
            print("name: " + name)
            m = importlib.import_module('eventHandlers.'+name.strip())
            cls = getattr(m, name.strip())
            self.eventHandlers.append(cls())

    def handleEvent(self, event):
        for handler in self.eventHandlers:
            print("=======================================" + str(type(handler)))
            self.pool.apply_async(handler, [event['type'], event['object'].metadata.name, event['object'].status])

    def watchLoop(self):
        v1 = client.BatchV1Api()
        w = watch.Watch()
        events = w.stream(v1.list_namespaced_job, "default", timeout_seconds=0)
        for event in events:
            print("Event >>>>>>>>>: %s, %s" % (event['type'], event['object'].metadata.name))
            self.handleEvent(event)

    def run(self):
        try:
            config.load_kube_config()
            self.loadHandlers()
            self.watchLoop()
        except KeyboardInterrupt:
            self.pool.close()
            self.pool.terminate()
        except:
            traceback.print_exc()


if __name__ == '__main__':
    cleaner = Cleaner()
    cleaner.run()
