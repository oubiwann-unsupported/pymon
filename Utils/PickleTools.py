class Pickling:

  def _savePickleFile(self, filename, data):
    '''
    More than one method needs to write data to a 
    file, so this privaledged method was created.
    '''
    from cPickle import dump

    if self.pickle_binary:
      file = open(filename, "wb+")
      dump(data, file, 1)
    else:
      file = open(filename, "w+")
      dump(data, file)
    file.close()

  def _loadPickleFile(self, filename):
    '''
    Read a pickled file.
    '''
    from cPickle import load

    if self.pickle_binary:
      file = open(filename, "rb")
    else:
      file = open(filename, "r")

    return load(file)

  def getPickleFiles(self):
    '''
    This method reads all the current tmp files
    '''
    import glob
    pattern = '%s/%s*%s' % (self.pickle_dir, self.pickle_prefix, self.pickle_sufix)
    
    return glob.glob(pattern)

  def _getPickledStatesSummary(self):
    '''
    This method reads all the current tmp files, unpickles
    them, and then displays the data for each monitored
    service.

    This method is not used during the monitoring process;
    it is used for reporting, such as a web interface.
    '''
    all_states = []
    for file in self.getPickleFiles():
      if self.debug:
        print "retrieving data from '%s'" % file
      old_data = self._loadPickleFile(file)
      for service, state in old_data.states.iteritems():
        try:
          #color = float(state)/float(last_state)
          if state == 1: hex = '#cc0000'
          elif state == 2: hex = '#cccc00'
          elif state == 3: hex = '#0000cc'
          elif state == 4: hex = '#00cc00'
          else: hex = "#cccccc"
          if self.debug:
            print service
            print state
            print old_data.last_state
          last_state = old_data.last_state[service]
          last_state = self.state_defs_lookup.get(last_state)
          current_state = self.state_defs_lookup.get(state)
          data = (state,
                  old_data.remote_host,
                  old_data.monitor_type.lower(),
                  service.lower(),
                  color,
                  hex,
                  current_state,
                  last_state,
                  old_data.msgs[service],
                  old_data.last_check,
                  old_data.last_ok,
                  old_data.last_warn,
                  old_data.last_err)
          if self.debug:
            print data
          all_states.append(data) 
        except:
          print "No last state for service %s" % service
    all_states.sort()
    if self.debug:
      for data in all_states:
        print data
    self.all_states = all_states
