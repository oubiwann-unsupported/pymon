from System.Monitoring import Monitoring
from Utils.LocalTools import LocalTools

class Monitor(Monitoring, LocalTools):

  def __init__(self, debug=0):
    '''
    This inherits from other classes
    '''
    Monitoring.__init__(self)
    self.monitor_type = ''
    self.state_counts = []
    self.state_list = []
    self.msg_template = ''
    self.sbj_template = ''
    self.debug = debug

  def hostsPingMonitor(self):
    '''
    the ping counts have already been obtained at this point, and
    now they have to be evaluated; this method sets the monitoring
    type to 'ping' and calls the general private evaluation method.
    Evaulation is a process of comparing the ping counts to 'warn'
    and 'error' thresholds set on the object.
    '''
    self.monitor_type = 'ping'
    self.state_counts = self.getPingCounts()
    self.state_list = self.host_list
    self.msg_template = 'There was a %s percent ping return from host %s'
    self.sbj_template = 'Service Monitor: %s %s (ping check)'
    self._doMonitor()

  def processMonitor(self):
    '''
    the process counts have already been obtained at this point, and
    now they have to be evaluated; this method sets the monitoring
    type to 'process' and calls the general private evaluation method.
    Evaulation is a process of comparing the process counts to 'warn'
    and 'error' thresholds set on the object.
    '''
    self.monitor_type = 'process'
    if self.remote_host == 'localhost':
      sbj_part = '(local %s check)' % self.monitor_type
    else:
      sbj_part = '(%s %s check)' % (self.remote_host, self.monitor_type)
    self.state_counts = self.matchProcess()
    self.state_list = self.match_list
    self.msg_template = 'There were %s %s processes'
    self.sbj_template = 'Service Monitor: %s %s ' + sbj_part
    self._doMonitor()

  def webSiteMonitor(self):
    '''
    this is a monitor for web sites
    '''
    self.monitor_type = 'web site'
    self.state_counts = self.getWebSiteCodes()
    self.state_list = self.site_list
    self.msg_template = 'Status code %s was returned from site %s'
    self.sbj_template = 'Service Monitor: %s %s (site check)'
    self._doMonitor()
