from System.Processes import Processes
from Internet.Mail import Mail
from Internet.Ping import HostsUp
from Internet.Site import Web
from Utils.PickleTools import Pickling

class Monitoring(HostsUp, Processes, Mail, Web, Pickling):

  def __init__(self, debug=0):
    '''
    This inherits from other classes
    '''
    Processes.__init__(self)
    HostsUp.__init__(self)
    Web.__init__(self)
    self.list_command = 'ps aux --columns 1000'
    self.notification_list = []
    self.sbj_template = 'Service Monitor: %s %s'
    self.mail_from = 'pymonitor@adytumsolutions.com'
    self.mailhost = '127.0.0.1'
    self.states = {}
    self.msgs = {}
    self.last_state = {}
    self.counts = {}
    self.storage_type = 'pickle'
    self.pickle_dir = '/tmp'
    self.pickle_prefix = 'pymon'
    self.pickle_sufix = 'pickle'
    self.pickle_binary = 0
    self.remote_host = 'localhost'
    self.remote_port = 0
    self.last_check = ''
    self.last_ok = ''
    self.last_warn = ''
    self.last_err = ''
    self.state_counts = []
    self.state_list = []
    self.monitor_type = ''
    self.debug = debug
    self.all_states = []
    self.summary_pymon = None
    self.summary_extapp = None
    self.titles = []

    self.state_defs = {
      'ERROR':      1,
      'WARN':       2,
      'RECOVERING': 3,
      'OK':         4,
    }

    self.state_defs_lookup = dict([[v,k] for k,v in self.state_defs.items()])
 
 
  def getStateData(self):
    '''
    This loops through the services that are being
    monitored and gets the current status for each
    service (OK, WARN, ERROR)

    This method is called by _doMonitor method, which
    in turn is called by individual monitoring type
    methods. The individual monitoring type set all
    properties specific to the monitoring type, most
    of which are needed by this method in order to 
    function properly.
    '''
    if self.debug:
      print "counts: %s" % self.state_counts
      print "list: %s" % self.state_list

    i = 0
    for count in self.state_counts:
      service  = self.state_list[i]

      err_lvl  = self.err_thresh[i]
      warn_lvl = self.warn_thresh[i]

      self.counts[service] = count
      if count < err_lvl:
        self.states[service] = self.state_defs['ERROR']
        self.last_err = self.getTimeStamp()
      elif count < warn_lvl:
        self.states[service] = self.state_defs['WARN']
        self.last_warn = self.getTimeStamp()
      else:
        self.states[service] = self.state_defs['OK']
        self.last_ok = self.getTimeStamp()
      i += 1

    return self.states

  def _getLastRun(self):
    '''
    Get the data from the last monitoring run
    '''
    try:
      return self.loadRunData(self.data_filename)
    except:
      return None
	
  def getTimeStamp(self):
    '''
    Create a simple timestamp used by other methods.
    '''
    from time import localtime, strftime
    
    return strftime("%Y.%m.%d-%H:%M.%S",localtime())

  def _doMonitor(self):
    '''
    This method performs the evaluations of monitor counts
    and compares them to threshold values
    '''

    i = sendit = 0
    msg = subj = ''
    self.data_filename = self._makeFileDataFileName()
    self.last_run = self._getLastRun()
    try:
      self.last_state = self.last_run.states
      self.last_check = self.last_run.last_check
      self.last_ok = self.last_run.last_ok
      self.last_warn = self.last_run.last_warn
      self.last_err = self.last_run.last_err
      if self.debug:
        print "Last State: %s" % self.last_state
        print "Last Check: %s" % self.last_check
        print "Last OK: %s" % self.last_ok
        print "Last Warn: %s" % self.last_warn
        print "Last Error: %s" % self.last_err

    except:
      pass
    self.getStateData()

    for service, state in self.states.iteritems():
      if self.debug:
        print "Service: %s" % service
        print "State: %s" % state

      state = self.state_defs_lookup.get(state)
      if self.debug:
        print"This state: %s" % state
      try:
        last_state = self.state_defs_lookup.get(self.last_state[service])
        if self.debug:
          print "Last State: %s" % last_state
      except:
        pass

      if state == 'ERROR':
        try: 
          if state != last_state: 
            sendit = 1
            if self.debug:
              print "State change; going to send mail"
          else: sendit = 0 
        except: pass 
      elif state == 'WARN':
        try: 
          if state != last_state: 
            sendit = 1
            if self.debug:
              print "State change; going to send mail"
          else: sendit = 0
        except: pass
      elif state == 'OK':
        try:
          if state != last_state:
            if last_state != 'RECOVERING':
              state = 'RECOVERING'
              self.states[service] = self.state_defs[state]
            sendit = 1
        except:
          sendit = 0

      if sendit:
        subj = self.sbj_template % (service, state)
        msg  = 'State: %s!\n' % (state)
        msg += self.msg_template % (self.counts[service], service)
        for mail_to in self.notification_list:
          if self.debug:
            print "getting ready to send mail to %s" % mail_to
            print "sending mail about service %s" % service
          self.mail(mail_to, self.mail_from, subj, msg, self.mailhost) 
      else:
        msg = self.msg_template % (self.counts[service], service)
      self.msgs[service] = msg
      sendit = 0
      i += 1
    self.last_check = self.getTimeStamp()
    self.saveRunData(self.data_filename)

  def _makeFileDataFileName(self):
    '''
    This is called from the _doMonitor method and thus has access to 
    all properties set by the *Monitor methods.
    '''
    from string import join, replace

    if self.titles:
      name_list = self.titles
    else:
      name_list = self.state_list
    if self.remote_host != 'localhost':
      mid = '%s-%s' % (self.remote_host, join(name_list, '-'))
    else:
      mid = join(name_list, '-')
    mid = '%s-%s' % (self.monitor_type, mid)
    mid = replace(mid, ' ', '_')
    filename = '%s/%s.%s.%s' % (self.pickle_dir, self.pickle_prefix, mid, self.pickle_sufix)
    if self.debug:
      print "generating filename service: %s" % filename

    return filename

  def saveRunData(self, filename):
    '''
    This saves all the data from the last run in a data
    file in the /tmp directory; data is pickled
    '''
    self._savePickleFile(filename, self)

  def loadRunData(self, filename):
    '''
    Reads all the data from the last run into
    the current monitoring instance
    '''
    self._loadPickleFile(filename)

  def getStatesSummary(self):
    '''
    Get summary data for the current states of all 
    monitored services.
    '''
    if self.storage_type == 'pickle':
      return self._getPickledStatesSummary()

  def getAllStates(self):
    if not self.all_states:
      self.getStatesSummary()
    return self.all_states
    
  def printAllStates(self):
    if not self.all_states:
      self.getStatesSummary()
    print self.all_states

  def saveSummaryData(self, filename=None):
    '''
    This saves all the summary data. 
    '''

    if not filename:
      filename = self.summary_pymon
    if self.debug:
      print filename

    data = self.getAllStates()
    if self.debug:
      print data

    if self.storage_type == 'pickle':
      self._savePickleFile(filename, data)

  def copySummaryData(self, orig_name=None, dest_name=None):
    '''
    This copies the summary data to a file that will be
    accessed by external applications, decreasing the 
    odds of hitting the race condition.
    '''

    from shutil import copy
    from os.path import exists

    if not (orig_name and dest_name):
      orig_name = self.summary_pymon
      dest_name = self.summary_extapp
    if self.debug:
      print (orig_name, dest_name)
  
    orig = None
    if not exists(orig_name):
      self.saveSummaryData()  
    copy(orig_name, dest_name)
