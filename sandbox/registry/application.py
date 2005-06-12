class Application(object):
  def __init__(self, name=None):
    self.name = name
  def setConfiguration(self, config):
    self.config = config
  def setState(self, state):
    self.state = state
  def getState(self):
    return self.state
  def setName(self, name=None):
    if not name and self.config:
        name = getattr(self.config, 'appname')
    self.name = name
  def getName(self):
    return self.name


