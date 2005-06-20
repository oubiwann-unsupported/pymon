import protocols
from registry import globalRegistry
from random import random

class Client(protocols.Protocol):
  def connect(self):
    self.establishConnection()
    print "connected..."
  def disconnect(self):
    print "disconnected..."
  def printData(self):
    data = {
        'a':int(random()*10), 
        'b':int(random()*10), 
        'c':int(random()*10),
    }
    globalRegistry.history.add(data)
    print globalRegistry.history.qsize()
    print globalRegistry.history.getLastRemoved()
    print "reg: %s" % globalRegistry
    print "data returned: %s\n" % data

