class Processes:

  def __init__(self):
    self.process_list = []
    self.list_command = ''
    self.match_list = []
    self.is_remote = 0

  def getProcessList(self, is_remote=0, host='', user='', passwd='', cmd=None):
    import commands
    if not cmd:
      try:
        cmd = self.command
      except:
        cmd = self.list_command
    self.process_list = commands.getoutput(cmd).split('\n')
    if self.debug:
      print cmd
      print self.process_list
      
    return self.process_list

  def getRemoteProcessList(self):
    host = self.remote_host
    user = self.remote_user
    cmd = '/usr/bin/ssh -l %s %s "ps aux --columns 1000"' % (user, host)

    return self.getProcessList(is_remote=1, host=host, user=user, cmd=cmd)

  def printProcesses(self):
    for proc in self.process_list:
      print proc

  def matchProcess(self, match_list=None):
    from string import count
    counts = []
    if not match_list:
      match_list = self.match_list
    if not self.process_list:
      self.getProcessList()
    for match in match_list: 
      counts.append(0)
      for process in self.process_list:
        try:
          process.index(match)
          match_index = match_list.index(match)
          counts[match_index] = counts[match_index] + 1
        except:
          not_found = 1
    return counts
