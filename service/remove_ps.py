# coding: utf-8
#from __future__ import print_function
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


class PsKiller(object):
    def removePs(self, psList):
        print 'deleting ps list: ' + str(psList)
        # TODO del k8s-ps, del keys
        config.load_kube_config()
        configuration = kubernetes.client.Configuration()
        delJobInstance = kubernetes.client.BatchV1Api(kubernetes.client.ApiClient(configuration))
        delSvcInstance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(configuration))
        body = kubernetes.client.V1DeleteOptions()
        body.propagation_policy = 'Foreground'
        namespace = ApiConfig().get("namespace", "tensorflow")
        for ps in psList:
            try:
                jobRes = delJobInstance.delete_namespaced_job(ps, namespace, body)
                print '----------------- ps jobRes: ' + str(jobRes)
                svcRes = delSvcInstance.delete_namespaced_service(ps, namespace, body)
                print '----------------- ps svcRes: ' + str(svcRes)
            except:
                traceback.print_exc()

    def removeWorker(self, workerList):
        print 'deleting worker list: ' + str(workerList)
        # TODO del k8s-ps, del keys
        config.load_kube_config()
        configuration = kubernetes.client.Configuration()
        delSvcInstance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(configuration))
        body = kubernetes.client.V1DeleteOptions()
        body.propagation_policy = 'Foreground'
        namespace = ApiConfig().get("namespace", "tensorflow")
        for worker in workerList:
            try:
                svcRes = delSvcInstance.delete_namespaced_service(worker, namespace, body)
                print '----------------- worker svcRes: ' + str(svcRes)
            except:
                traceback.print_exc()

    def run(self):
        try:
            rc = RedisHelper().getRedis()
            while True:
                res = rc.blpop(ApiConfig().get("event", "delete_queue"), 0)
                print '------------------ get res: ' + str(res)
                jsInfo= res[1]
                print '--------------  get info: ' + str(jsInfo)
                infoMap = json.loads(jsInfo)
                self.removePs(infoMap.get('ps', []))
                self.removeWorker(infoMap.get('worker', []))
        except KeyboardInterrupt:
            pass
        except:
            traceback.print_exc()


if __name__ == '__main__':
    cleaner = PsKiller()
    cleaner.run()
