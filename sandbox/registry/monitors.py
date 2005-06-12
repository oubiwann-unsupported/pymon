import clients

class Monitor(object):
  def run(self):
    client = clients.Client()
    client.connect()
    client.disconnect()
    client.printData()
