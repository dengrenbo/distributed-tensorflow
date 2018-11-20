# coding: utf-8
from EventHandler import EventHandler
from util.ApiConfiger import ApiConfig
from util.RedisHelper import RedisHelper
import json
import re
import traceback

class CleanJobHandler(EventHandler):
    psPt = "tf-([0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12})-ps-([0-9].*)-([0-9].*)"
    workerPt = "tf-([0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12})-worker-([0-9].*)-([0-9].*)"

    def searchPattern(self, p, s):
        res = re.match(p, s)
        if not res:
            return None, None, None
        return res.group(1), res.group(2), res.group(3)

    '''
    tf-3e8f3702-d10b-11e8-abe4-fa163ef8da8a-[ps/worker]-0-1
    '''
    def addEvent(self, objName, eStatus):
        print '*************** CleanJobHandler: ' + str(objName)
        rc = RedisHelper().getRedis()
        tfId, curSeq, cnt = self.searchPattern(CleanJobHandler.psPt, objName)
        if tfId:
            rc.hsetnx(ApiConfig().get("event", "ps_key"), tfId, cnt)
        else:
            tfId, curSeq, cnt = self.searchPattern(CleanJobHandler.workerPt, objName)
            if tfId:
                rc.hsetnx(ApiConfig().get("event", "worker_key"), tfId, cnt)

    '''
    tf-3e8f3702-d10b-11e8-abe4-fa163ef8da8a-[ps/worker]-0-1
    {3e8f3702-d10b-11e8-abe4-fa163ef8da8a: 0}
    '''
    def modifEvent(self, objName, eStatus):
        print '*************** CleanJobHandler modify event: ' + str(objName)
        rc = RedisHelper().getRedis()
        tfId, curSeq, cnt = self.searchPattern(CleanJobHandler.psPt, objName)
        if tfId:
            # ps may be shutdown itself through singal from worker
            print 'ps modified'
        else:
            tfId, curSeq, cnt = self.searchPattern(CleanJobHandler.workerPt, objName)
            if not tfId:
                return
            if eStatus.succeeded and eStatus.succeeded == 1:
                curCount = rc.hincrby(ApiConfig().get("event", "worker_key"), tfId, -1)
                if (int(curCount) == 0):
                    print 'all worker done, clean ...'
                    psCnt = rc.hget(ApiConfig().get("event", "ps_key"), tfId)
                    print 'psCnt: ' + psCnt
                    allPs = ['tf-'+tfId+'-ps-'+str(i)+'-'+psCnt for i in xrange(int(psCnt))]
                    allWorker = ['tf-'+tfId+'-worker-'+str(i)+'-'+cnt for i in xrange(int(cnt))]
                    tfInfo = {'ps': allPs, 'worker': allWorker}
                    print 'tfInfo: ' + str(tfInfo)
                    try:
                        pushRes = rc.rpush(ApiConfig().get("event", "delete_queue"), json.dumps(tfInfo))
                        print 'pushRes: ' + str(pushRes)
                    except:
                        traceback.print_exc()
                else:
                    print 'one tf worker done successfully ......'
            else:
                # TODO failed
                pass

    def delEvent(self, objName, eStatus):
        print '************* CleanJobHandler delete event: ' + str(objName)
        rc = RedisHelper().getRedis()
        tfId, seq, cnt = self.searchPattern(CleanJobHandler.psPt, objName)
        if tfId:
            print 'delete event ps tfId: ' + tfId
            psCurCount = rc.hincrby(ApiConfig().get("event", "ps_key"), tfId, -1)
            if (int(psCurCount) == 0):
                # TODO record successful tfId
                print 'tfId successfully done'
                rc.hdel(ApiConfig().get("event", "ps_key"), tfId)
                rc.hdel(ApiConfig().get("event", "worker_key"), tfId)
