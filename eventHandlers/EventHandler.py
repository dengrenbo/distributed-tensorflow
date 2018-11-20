# coding: utf-8
class EventHandler(object):

    def __call__(self, eType, objName, eStatus):
        print '@@@@@@@@@@@ eventHandler type: ' + eType + ', name: ' + objName
        if eType == "ADDED":
            self.addEvent(objName, eStatus)
        elif eType == "MODIFIED":
            self.modifEvent(objName, eStatus)
        elif eType == "DELETED":
            self.delEvent(objName, eStatus)
        else:
            self.errorEvent(objName, eStatus)

    def addEvent(self, objName, eStatus):
        print 'do nothing'

    def delEvent(self, objName, eStatus):
        print 'do nothing'

    def modifEvent(self, objName, eStatus):
        print 'do nothing'

    def errorEvent(self, objName, eStatus):
        print 'do nothing'

