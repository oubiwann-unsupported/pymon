class LocalTools:

  def getPasswdFromFile(self, filename):
    return file(filename).readline()
