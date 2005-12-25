from datetime import datetime
from email.MIMEText import MIMEText

import dispatch

from zope.interface import implements

from twisted.spread import pb
from twisted.internet import reactor
from twisted.web.client import HTTPClientFactory
from twisted.web.client import PartialDownloadError
from twisted.internet.defer import TimeoutError
from twisted.internet.protocol import ClientFactory

from adytum.util.uri import Uri

from config import cfg
from registry import globalRegistry
from application import MonitorState, History
from workflow import service as workflow
from clients import base, ping, http, ftp, smtp
import utils
from utils import log

class AbstractFactory(object):
    '''
    A class for generating a specific type of monitor, depending
    on the passed monitor type.

    The monitors are really client factories, and hold configuration
    and other data that the clients need or have use for.
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

    [ makeMonitor.when("self.type == 'http_status'") ]
    def makeHttpStatusMonitor(self):
        monitor = HttpStatusMonitor(self.uid)
        return monitor

    [ makeMonitor.when("self.type == 'http_text'") ]
    def makeHttpTextMonitor(self):
        monitor = HttpTextMonitor(self.uid)
        return monitor

    [ makeMonitor.when("self.type == 'ftp'") ]
    def makeFtpMonitorMonitor(self):
        monitor = FtpMonitor(self.uid)
        return monitor

    [ makeMonitor.when("self.type == 'smtp_status'") ]
    def makeSmtpStatusMonitor(self):
        monitor = SmtpStatusMonitor(self.uid)
        return monitor

    [ makeMonitor.when("self.type == 'smtp_mail'") ]
    def makeSmtpMailMonitor(self):
        monitor = SmtpMailMonitor(self.uid)
        return monitor

class MonitorMixin(object):

    def __init__(self, uid):
        # XXX why does all this stuff have to be stored in the object? 
        # That's a lot of memory utilization... duplication. We've got a 
        # global registry -- why not use it? We've got lookup function,
        # and the lookups are operating against the in-memory registry.
        # It may be a little slower, but I think it will be better to 
        # decrease memory utilization of objects. pymon will scale 
        # better... will be able to take on more service checks.
        self.uid = uid
        self.cfg = cfg
        self.service_type = utils.getTypeFromUri(self.uid)
        self.service = getattr(self.cfg.services, self.service_type)
        self.workflow = workflow.ServiceState(workflow.state_wf)
        self.history = History()
        self.state = MonitorState(uid)
        self.statedefs = self.cfg.state_definitions
        self.service_cfg = utils.getEntityFromUri(self.uid)
        self.type_defaults = self.service.defaults
        if self.service_cfg.interval:
            interval = self.service_cfg.interval
        else:
            interval = self.type_defaults.interval
        self.interval = interval

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.uid)

    def __call__(self):
        # update the configuration in case it has changed
        uri = Uri(self.uid)
        self.service_cfg = utils.getEntityFromUri(self.uid)
        self.type_defaults = utils.getDefaultsFromUri(self.uid)

        self.state.backup()
        maint_window = False
        try:
            if (self.service_cfg.scheduled_downtime['start'].timetuple() <
                datetime.now().timetuple() <
                self.service_cfg.scheduled_downtime['end'].timetuple()):
                maint_window = True
        except TypeError:
            pass
        except AttributeError:
            if self.service_cfg == None:
                log.error("Configuration should not be none!")
                log.debug("MonitorMixin: \n%s\n%s\n%s" % (self, 
                    dir(self), self.__dict__))
        if maint_window:
            # XXX These two chunks of state info access need to be moved 
            # out of here... and made less eyesoreingly redundant. 
            # There's another set of XXX's that discuss this in general
            # elsewhere. There are also notes in the TODO.
            msg = "Service %s has been disabled during maintenance."
            log.warning(msg % self.uid)
            self.state['current status'] = self.statedefs.maintenance
            self.state['current status name'] = 'maintenance'
            self.state['count maintenance'] = 1
            self.state['node'] = uri.getAuthority().getHost()
            self.state['service'] = uri.getScheme().replace('_', ' ')
            org = self.service_cfg.org
            if org:
                self.state['org'] = org
            globalRegistry.factories[self.uid].state = self.state            
        elif self.service_cfg.enabled:
            reactor.connectTCP(*self.reactor_params)
        else:
            msg = "Service %s has been disabled; not checking."
            log.warning(msg % self.uid)
            self.state['current status'] = self.statedefs.disabled
            self.state['current status name'] = 'disabled'
            self.state['count disabled'] = 1
            self.state['node'] = uri.getAuthority().getHost()
            self.state['service'] = uri.getScheme().replace('_', ' ')
            org = self.service_cfg.org
            if org:
                self.state['org'] = org
            globalRegistry.factories[self.uid].state = self.state

    def setInterval(self, seconds=None):
        if seconds:
            self.interval = seconds
        elif not self.interval:
            try:
                interval = utils.getEntityFromUri(self.uid).interval
            except AttributeError:
                interval = utils.getDefaultsFromUri(self.uid).interval
            self.interval = interval

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
        self.page_url = 'http://%s/' % self.service_cfg.uri
        # XXX write a getTimeout method
        #timeout = self.service_cfg.timeout
        #timeout = self.type_defaults.timeout
        self.host = Uri(uid).getAuthority().getHost()
        self.agent = self.cfg.user_agent_string
        self.method = 'HEAD'
        self.status = None
        # XXX write a method to get the http port from defaults or service config
        #port = self.service_cfg.http_port
        port = self.type_defaults.remote_port
        self.reactor_params = (self.host, port, self)

    def __repr__(self):
        """
        We need to overried the __repr__ in HTTPClientFactory; 
        inheriting from MonitorMixin won't do it.
        """
        return "<%s: %s>" % (self.__class__.__name__, self.uid)

    def __call__(self):
        HTTPClientFactory.__init__(self, self.page_url, method=self.method, 
            agent=self.agent, timeout=int(self.type_defaults.interval))
        MonitorMixin.__call__(self)
        d = self.deferred
        d.addCallback(self.logStatus)
        d.addErrback(self.errorHandlerPartialPage)
        d.addErrback(self.errorHandlerTimeout)

    def clientConnectionFailed(self, connector, reason):
        self.message = reason.getErrorMessage()
        log.error("Failed: %s" % self.message)
        self._setupNullClient()

    def logStatus(self):
        log.info('Return status: %s' % self.status)

    def errorHandlerPartialPage(self, failure):
        failure.trap(PartialDownloadError)
        log.error("Hmmm... got a partial page...")
        log.debug('Here is the return status: %s' % self.status)

    def errorHandlerTimeout(self, failure):
        failure.trap(TimeoutError)
        self.message = failure.getErrorMessage()
        log.error("Timeout: %s" % self.message)
        self._setupNullClient()
    
    def _setupNullClient(self):
        '''
        This needs to be called anytime we didn't get a connection. 
        Rules processing occurs 
        '''
        self.status = '0'
        log.debug('Config: %s' % self.service_cfg)
        self.original_protocol = self.protocol
        log.debug('Original Protocol: %s' % self.original_protocol)
        self.protocol = base.NullClient()
        log.debug('New Protocol: %s' % self.protocol)
        self.protocol.makeConnection(self)
        self.protocol = self.original_protocol
        log.debug('Reverted Protocol: %s' % self.protocol)

class PingMonitor(pb.PBClientFactory, MonitorMixin):

    protocol = ping.PingClient

    def __init__(self, uid):
        pb.PBClientFactory.__init__(self)
        MonitorMixin.__init__(self, uid)

        # ping config options setup
        self.defaultcfg = self.service.defaults
        self.checkdata = self.service_cfg

        # get the info in order to make the next ping
        self.binary = self.defaultcfg.binary
        count = '-c %s' % self.defaultcfg.count
        host = Uri(self.uid).getAuthority().getHost()
        self.args = [count, host]

        #options = ['ping', '-c %s' % count, '%s' % host]
        port = cfg.agents.port
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

class FtpMonitor(ClientFactory, MonitorMixin):

    protocol = ftp.FtpStatusClient

    def __init__(self, uid):
        MonitorMixin.__init__(self, uid)
        self.host = Uri(uid).getAuthority().getHost()
        self.port = int(self.service_cfg.port)
        self.username = self.service_cfg.username
        self.password = self.service_cfg.password
        self.passive = self.service_cfg.passive
        self.return_code = 0
        self.reactor_params = (self.host, self.port, self)

    def __call__(self):
        MonitorMixin.__call__(self)


    def clientConnectionLost(self, connector, reason):
        log.debug("Connection Lost:", reason)

    def clientConnectionFailed(self, connector, reason):
        self.return_code = 100
        log.error("Connection Failed:", reason.getErrorMessage())
        self.message = reason.getErrorMessage()
        self.status = 'NA'
        self.protocol = base.NullClient()
        self.protocol.factory = self
        self.protocol.makeConnection()

class SmtpStatusMonitor(ClientFactory, MonitorMixin):

    protocol = smtp.SmtpStatusClient

    def __init__(self, uid):
        MonitorMixin.__init__(self, uid)
        self.host = Uri(uid).getAuthority().getHost()
        self.port = int(self.service_cfg.port)
        self.identity = self.service_cfg.identity 
        self.status = 0
        self.reactor_params = (self.host, self.port, self)

    def buildProtocol(self, addr):
        p = self.protocol(identity=self.identity, logsize=10)
        p.factory = self
        return p

    def __call__(self):
        MonitorMixin.__call__(self)

    def clientConnectionFailed(self, connector, reason):
        log.error("Connection Failed: %s " % reason.getErrorMessage())
        self.message = reason.getErrorMessage()
        self.status = 'NA'
        self.protocol = base.NullClient()
        self.protocol.factory = self
        self.protocol.makeConnection()


class SmtpMailMonitor(ClientFactory, MonitorMixin):

    protocol = smtp.SmtpMailClient

    def __init__(self, uid):
        MonitorMixin.__init__(self, uid)
        self.host = Uri(uid).getAuthority().getHost()
        self.port = int(self.service_cfg.port)
        self.identity = self.service_cfg.identity
        self.status = 0
        self.mail_from = self.service_cfg.mail_from
        self.mail_to = self.service_cfg.mail_to
        self.reactor_params = (self.host, self.port, self)
    
        # Construct an email message with the appropriate headers
        msg = MIMEText("Pymon SMTP server mail check email")
        msg['Subject'] = "Pymon Test Email"
        msg['From'] = self.mail_from
        msg['To'] = self.mail_to
    
        self.mail_data = msg.as_string()

    def buildProtocol(self, addr):
        p = self.protocol(identity=self.identity, logsize=10)
        p.factory = self
        return p

    def __call__(self):
        MonitorMixin.__call__(self)

    def clientConnectionFailed(self, connector, reason):
        log.error("Connection Failed: %s " % reason.getErrorMessage())
        self.message = reason.getErrorMessage()
        self.status = 'NA'
        self.protocol = base.NullClient()
        self.protocol.factory = self
        self.protocol.makeConnection()

