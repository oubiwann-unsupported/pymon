from adytum.app.pymon import config

class LocalTools:

  def getPasswdFromFile(self, filename):
    return file(filename).readline()

def getService(db_type):
    from adytum.app.pymon.api import storage
    return eval('storage.%s.Service' % db_type)

def updateDatabase(data):
    pass
