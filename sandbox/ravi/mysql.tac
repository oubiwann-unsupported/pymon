from twisted.application import service, internet
from twisted.internet import reactor
from twisted.spread import pb
from twisted.internet import reactor
from twisted.enterprise import adbapi

INTERVAL = 10
class MySQLClient(pb.Root):

    def conectionMade(self):
        pb.Broker.connectionMade(self)
        self.host = 'localhost'
        self.username = 'test'
        self.password  = 'test'
        self.pool = adbapi.ConnectionPool("MySQLdb", self.host,
                                          self.username, self.password)

    def remote_execute(self, statement, *args):
        return self.factory.pool.runQuery(statement, args)

    def connectionLost(self, reason):
        print reason

class Monitor(pb.PBClientFactory):

    protocol = MySQLClient

    def __init__(self):
        pb.PBClientFactory.__init__(self)
        self.host = 'localhost'
        self.port = 3306
        self.sql = 'show status'

    def __call__(self):
        reactor.connectTCP(self.host, self.port, self)
        d = self.getRootObject()
        d.addErrback(self.printError)
        d.addCallback(self.executeCmd)
        d.addCallback(self.getCmdReturn)

    def printError(self, error):
        print error

    def executeCmd(self, pbobject):
        return pbobject.callRemote("execute", self.sql)

    def getCmdReturn(self, results):
        self.data = results
        print results
        self.disconnect()

    def clientConnectionFailed(self, connector, reason):
        self._failAll(reason)
        print reason

application = service.Application("pymon")
pymonServices = service.IServiceCollection(application)

monitor = Monitor()
server = internet.TimerService(INTERVAL, monitor)
server.setServiceParent(pymonServices)
