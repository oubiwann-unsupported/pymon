from twisted.internet import protocol

from adytum.app.pymon.storage import sql

def isInRange(datum, incl_range):

    mn, mx = incl_range.split(',')
    if int(mn) <= int(datum) <= int(mx):
        return True
    return False

def getStatus(datum, cfg):
    pass

class PyMonProcess(protocol.ProcessProtocol):

    def __init__(self):
        self.data = ''
        self.pid = ''

    def connectionMade(self):
        self.pid = self.transport.pid
        print "opened process %s..." % self.pid
        self.transport.closeStdin() 

    def outReceived(self, data):
        print "recieved data from process %d (%d bytes)" % (self.pid, len(data))
        self.data = self.data + data

    def errReceived(self, data):
        print "got error from process (%d bytes)" % len(data)
        print data

    def outConnectionLost(self):
        print "closed process stdout."

    def errConnectionLost(self):
        print "closed process stderr."

    def processEnded(self, status_object):
        print "process %d complete (status %d)" % (self.pid, status_object.value.exitCode)
        print self.data

class PyMonHTTPClient(protocol.Protocol):
    '''
    '''
    def __init__(self, cfg):
       self.cfg = cfg
       self.data = ''

    def connectionMade(self):
        #self.transport.write("GET /\r\n")
        self.transport.write("HEAD / HTTP/1.0 \r\n\r\n")

    def dataReceived(self, data):
        self.data = data

    def connectionLost(self, reason):
        from adytum.net.http.request import HeaderParser
         
        parse = HeaderParser(self.data)
        status = parse.getReturnStatusInteger()

        uid = self.cfg['data']['__name__']
        host = self.cfg['data']['destination host']
        msg = self.cfg['defaults']['message template'] % (host, status)
       
        if status in self.cfg['defaults']['ok threshold'].split(','):
            #raise str(self.cfg['constants'])
            status = self.cfg['constants']['states']['ok']
        elif status in self.cfg['defaults']['warn threshold'].split(','):
            status = self.cfg['constants']['states']['warn']
        elif status in self.cfg['defaults']['error threshold'].split(','):
            status = self.cfg['constants']['states']['error']
        else:
            status = -1

        # prepare data for insert/update
        data = {
            'uniqueID': uid,
            'serviceHost': host,
            'serviceType': self.cfg['data']['service type'],
            'serviceName': self.cfg['defaults']['service name'],
            'serviceStatus': status,
            'serviceMessage': msg,
        }
        sql.updateDatabase(data)

class PyMonPing(PyMonProcess):

    def __init__(self, cfg):
        self.cfg = cfg
        self.data = ''
        self.pid = ''

    def processEnded(self, status):

        from adytum.net.ping import OutputParser
        
        parse = OutputParser(self.data)
        loss = parse.getPingLoss()
        gain = parse.getPingGain()

        uid = self.cfg['data']['__name__']
        host = self.cfg['data']['destination host']
        msg = self.cfg['defaults']['message template'] % (gain, host)
        
        if isInRange(gain, self.cfg['defaults']['ok threshold']):
            #raise str(self.cfg['constants'])
            status = self.cfg['constants']['states']['ok']
        elif isInRange(gain, self.cfg['defaults']['warn threshold']):
            status = self.cfg['constants']['states']['warn']
        elif isInRange(gain, self.cfg['defaults']['error threshold']):
            status = self.cfg['constants']['states']['error']
        else:
            status = -1

        # prepare data for insert/update
        data = {
            'uniqueID': uid,
            'serviceHost': host,
            'serviceType': self.cfg['data']['service type'],
            'serviceName': self.cfg['defaults']['service name'],
            'serviceStatus': status,
            'serviceMessage': msg,
        }
        #print data
        updateDatabase(data)


class PyMonHTTPClientFactory(protocol.ClientFactory):
    '''
    '''

    def __init__(self, cfg):
        self.cfg = cfg
        self.data = ''
        self.pid = ''

    def startedConnecting(self, connector):
        print 'Started to connect.'

    def buildProtocol(self, addr):
        print 'Connected.'
        return PyMonHTTPClient(self.cfg)

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
