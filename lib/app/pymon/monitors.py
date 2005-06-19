import dispatch
from zope.interface import implements
from twisted.internet import reactor
from twisted.spread import pb
from twisted.web.client import HTTPClientFactory, PartialDownloadError
from adytum.util.uri import Uri


from registry import globalRegistry
from application import State, History
from workflow import service as workflow
from clients import ping, http
import utils

class AbstractFactory(object):
    '''
    A class for generating a specific type of monitor,
    depending on the passed monitor type.

    The monitors are really client factories, and hold
    configuration and other data that the clients need or
    have use for.
    '''
    def __init__(self, uid):

        self.uid = uid
        self.type = utils.getTypeFromUri(uid)

    [ dispatch.generic() ]
    def makeMonitor(self):
        '''
        Generic method for client creation.
        '''

    [ makeMonitor.when("self.type == 'ping'") ]
    def makePingMonitor(self):
        monitor = PingMonitor(self.uid)
        return monitor

    [ makeMonitor.when("self.type == 'http status'") ]
    def makeHttpStatusMonitor(self):
        monitor = HttpStatusMonitor(self.uid)
        return monitor

    [ makeMonitor.when("self.type == 'http text'") ]
    def makeHttpTextMonitor(self):
        monitor = HttpTextMonitor(self.uid)
        return monitor

class MonitorMixin(object):

    def __init__(self, uid):
        self.uid = uid
        self.cfg = globalRegistry.config
        self.service_type = utils.getTypeFromUri(self.uid)
        self.service = self.cfg.services.service(type=self.service_type)
        self.interval = None
        self.setInterval()
        self.workflow = workflow.ServiceState(workflow.state_wf)
        self.history = History()
        self.state = State()
        self.statedefs = self.cfg.constants.states
        self.mailcfg = self.cfg.system.mail
        self.service_cfg = utils.getEntityFromUri(self.uid)
        self.type_defaults = self.cfg.services.service(type=self.service_type).defaults

    def __call__(self):
        reactor.connectTCP(*self.reactor_params)

    def setInterval(self, seconds=None):
        if seconds:
            self.interval = seconds
        elif not self.interval:
            interval = utils.getEntityFromUri(self.uid).interval
            if not interval:
                interval = utils.getDefaultsFromUri(self.uid).interval
            self.interval = int(interval)

    def getInterval(self):
        return self.interval

class HttpTextMonitor(HTTPClientFactory, MonitorMixin):
    
    def __init__(self, uid):
        MonitorMixin.__init__(self, uid)
        self.page_url = ''
        self.text_check = ''
        self.checkdata = self.service.entries.entry(uri=self.uid)
        self.reactor_params = ()

class HttpStatusMonitor(HTTPClientFactory, MonitorMixin):
    
    protocol = http.HttpStatusClient

    def __init__(self, uid):
        MonitorMixin.__init__(self, uid)
        page_url = 'http://%s/' % self.service_cfg.uri
        # XXX write a getTimeout method
        #timeout = self.service_cfg.timeout
        #timeout = self.type_defaults.timeout
        host = Uri(uid).getAuthority().getHost()
        agent = self.cfg.web.agent_string
        method = 'HEAD'
        # XXX write a method to get the http port from defaults or service config
        #port = self.service_cfg.http_port
        port = int(self.type_defaults.http_port)
        self.reactor_params = (host, port, self)
        HTTPClientFactory.__init__(self, page_url, method=method, 
            agent=agent)#, timeout=timeout)

    def __call__(self):
        MonitorMixin.__call__(self)
        d = self.deferred
        d.addCallback(self.printStatus)
        d.addErrback(self.errorHandlerPartialPage)

    def printStatus(self):
        print 'Here is the return status: %s' % self.status

    def errorHandlerPartialPage(self, failure):
        failure.trap(PartialDownloadError)
        print "Hmmm... got a partial page..."
        print 'Here is the return status: %s' % self.status

class PingMonitor(pb.PBClientFactory, MonitorMixin):

    protocol = ping.PingClient

    def __init__(self, uid):
        pb.PBClientFactory.__init__(self)
        MonitorMixin.__init__(self, uid)

        # ping config options setup
        self.defaultcfg = self.service.defaults
        self.checkdata = self.service.entries.entry(uri=self.uid)

        # get the info in order to make the next ping
        self.binary = self.defaultcfg.binary
        count = '-c %s' % self.defaultcfg.count
        host = Uri(self.uid).getAuthority().getHost()
        self.args = [count, host]

        #options = ['ping', '-c %s' % count, '%s' % host]
        port = int(globalRegistry.config.system.agents.port)
        self.reactor_params = ('127.0.0.1', port, self)

    def __call__(self):
        MonitorMixin.__call__(self)
        d = self.getRootObject()
        d.addCallback(self.pingHost)
        d.addCallback(self.getPingReturn)

    def pingHost(self, pbobject):
        return pbobject.callRemote('call', self.binary, self.args)

    def getPingReturn(self, results):
        self.data = results
        #print dir(self)
        #print results
        self.disconnect()

    def clientConnectionLost(self, connector, reason, reconnecting=1):
        """Reconnecting subclasses should call with reconnecting=1."""
        if reconnecting:
            # any pending requests will go to next connection attempt
            # so we don't fail them.
            self._broker = None
            self._root = None
        else:
            self._failAll(reason) 

