################################
# Read Service Monitoring Data #
################################

# this is designed to be used by Zope as an
# External Method
def show_states(self):
  from cPickle import load

  pickle_binary = 1
  filename = '/tmp/pymon.summary.external'
  if pickle_binary:
    file = open(filename, "rb")
  else:
    file = open(filename, "r")
  return load(file)
