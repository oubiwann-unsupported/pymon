from commands import getoutput 

class HostsUp:

  def __init__(self, host='', counts=2, debug=0):
    self.host = host                 # this can be either IP or hostname
    self.ping_counts = counts
    self.ping_wait = 1
    self.host_list = ''
    self.debug = debug

  #def isUp(self):

  def _pingHost(self):
    #ping_command = '/bin/ping -c %d -i %s %s' % (self.ping_counts, self.ping_wait, self.host)
    ping_command = '/usr/sbin/hping --fast --quiet -c %d %s' % (self.ping_counts, self.host)
    try:
      self.ping_output = getoutput(ping_command) 
    except:
      print 'Could not get output of command (%s)' % str(self.ping_output)

    return self.ping_output
    
  def _parsePingOutput(self):
    '''
    get the status line of output, the one that gives
    percent lost/packet drops. It's comma separated,
    with the following values:
      sent, received, % loss[, total time]
    '''
    lines = self.ping_output.splitlines()
    try:
      #self.ping_status = lines[-2].split(',')
      self.ping_status = lines[2].split(',')
    except:
      print 'could not get ping status (%s)' % str(lines)
      self.ping_status = [None,None,None]

    return self.ping_status

  def getPingCounts(self):
    ''' 
    get the ping counts for each host, where the counts show how
    good the network connection is to the host by subtracting the
    percent loss from 100%.
    '''
    counts = [] 
    for host in self.host_list:
        self.pinger = HostsUp(host=host, counts=16, debug=self.debug)
        counts.append(100 - int(self.pinger.getPingLoss()))
    
    return counts

  def getPingLoss(self):
    '''
    this returns a percentage, the percentage packet loss
    from the ping command run against the host
    '''
    self.ping_output = []
    self._pingHost()
    parse_output = self._parsePingOutput()
    if self.debug:
      print parse_output
    self.ping_percent = self.ping_status[2].split('%')[0]

    return self.ping_percent

  def getHostList(self):
    '''
    This method was originally created to be compatible with
    the process monitoring class; however, since they (process
    and host monitoring) have different behaviors at a deep 
    level, it isn't used in the intended way anymore and may
    go away at some point.
    '''

    #print self.host_list
    return self.host_list

  def matchHost(self):
    '''
    This method was originally created to be compatible with
    the process monitoring class; however, since they (process
    and host monitoring) have different behaviors at a deep 
    level, it isn't used in the intended way anymore and may
    go away at some point.
    '''

    #print self.host_list
    return self.host_list
