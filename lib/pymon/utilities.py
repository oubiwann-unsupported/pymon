from pymon import config

class LocalTools:

  def getPasswdFromFile(self, filename):
    return file(filename).readline()

def getService(db_type):
    from pymon.api import storage
    return eval('storage.%s.Service' % db_type)

def updateDatabase(data):
    pass

def isInRange(datum, incl_range):

    mn, mx = incl_range.split(',')
    if int(mn) <= int(datum) <= int(mx):
        return True
    return False

def getStatus(datum, cfg):
    pass

