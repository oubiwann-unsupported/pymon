#!/usr/bin/env python
import sys
from socket import gethostbyaddr
from optparse import OptionParser

from twisted.internet import task
from twisted.internet import defer
from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ClientFactory
from twisted.python.filepath import FilePath

try:
    from netcidr import CIDR, Networks
except ImportError:
    print ('\nYou must have NetCIDR installed for your version of python ' +
           'in order to run this tool.')
    sys.exit()

from pymon.utils import getSimplePlural


usage = '''%prog [options] netBlock[,netBlock2[,...]] startPort,endPort

You need to pass the CIDR block(s) that define the network(s)
you want to scan as well as the port range to be scanned for
each host. The port range must be two comma-separated integers.
For example:
    %prog [options] 192.168.4.0/24 1,8080
    %prog [options] 172.16.0.0/16,172.29.13.0/24,10.1.24.0/26 21,1024


There are two parameters that control the rate at which the connections to
servers are made: batchSize and timeout. However, all parameters affect the
number of files opened in your os: with enough hosts and ports, a large batch
size and a small timeout, you could easily max out the number of open files on
your system. Please keep that in mind.

I have found that for hosts over a good internet connection, a timeout of 1
second usually gives enough time to make a connection. However, this can take
quite a while with a large number of ports per host. I have found the following
works well in general for internet discovery:
  %prog --batchSize=100 --timeout=1 1.2.3.4/24 1,1000
On my machine, that takes about 12 seconds.

For local networks, however, we don't have to worry so much about latency.
Connections are made and closed more quickly, leaving fewer open files in a
smaller period of time. Scanning large network blocks can go very quickly. I've
found the following works well on my corporate network:
  %prog --batchSize=200 --timeout=0.1 10.2.3.4/24 1,10000
'''

optp = OptionParser(usage=usage)
optp.set_defaults(ports='1,1000', batchSize=100, timeout=0.1, verbose=False,
                  spew=False, debug=False)
optp.add_option('-s', '--batchSize', dest='batchSize')
optp.add_option('-t', '--timeout', dest='timeout')
optp.add_option('-v', '--verbose', dest='verbose', action='store_true')
optp.add_option('-p', '--spew', dest='spew', action='store_true')
optp.add_option('-d', '--debug', dest='debug', action='store_true')
(opts, args) = optp.parse_args()

if len(args) < 2:
    optp.error('You must pass at lease a netblock and a range of ports.')
blocks = args[0].split(',')
ports = args[1].split(',')
if len(ports) != 2:
    optp.error('You must provide two ports in the port range.')
try:
    ports = [int(x) for x in ports]
except ValueError:
    optp.error('Ports must be integers.')

TCPPingServiceConfigTemplate = '''
<ping-tcp-check>
    uri     %s
    ports   %s
    enabled true
</ping-tcp-check>
'''

def printError(err):
    print '\nError:\n'
    if opts.debug:
        print err
    else:
        print '\t%s' % err.getErrorMessage()
    print '\n'


class ScanProtocol(Protocol):

    def connectionMade(self):
        self.factory.deferred.callback("success")
        self.transport.loseConnection()


class ScanFactory(ClientFactory):

    protocol = ScanProtocol

    def __init__(self):
        self.deferred = defer.Deferred()

    def clientConnectionFailed(self, connector, reason):
        self.deferred.errback(reason)

    def clientConnectionLost(self, connector, reason):
        pass


class Scanner(object):
    '''
    '''
    def __init__(self, hosts, portRange, batchSize=50, timeout=1):
        self.hosts = hosts
        portRange[1] += 1
        self.portRange = portRange
        self.batchSize = int(batchSize)
        self.timeout = float(timeout)
        self.data = {
            'success': {},
            'failure': {},
        }

    def run(self):
        d = self.doScans()
        d.addCallback(self.doReport)
        d.addCallback(self.writeConfigs)
        d.addErrback(printError)
        reactor.run()

    def doScans(self):
        '''
        We use the Twisted task cooperator here to control the number of
        deferrds (and therefore connections) created at once, thus providing a
        way for systems to use the script efficiently.
        '''
        coop = task.Cooperator()
        def scanHosts():
            for host in self.hosts:
                for port in xrange(*self.portRange):
                    yield self.doFactory(host, port)
        scans = scanHosts()
        self.scans = defer.DeferredList(
            [coop.coiterate(scans) for i in xrange(self.batchSize)])
        return self.scans

    def doFactory(self, host, port):
        factory = ScanFactory()
        if opts.spew:
            print "Preparing connection for %s:%s ..." % (host, port)
        reactor.connectTCP(host, port, factory, self.timeout)
        d = factory.deferred
        d.addCallback(self.recordConnection, host, port)
        d.addErrback(self.recordFailure, host, port)
        return d

    def recordConnection(self, result, host, port):
        if opts.verbose or opts.spew:
            print "Connected to %s:%s ..." % (host, port)
        hostData = self.data['success'].setdefault(host, [])
        hostData.append(port)

    def recordFailure(self, failure, host, port):
        hostData = self.data['failure'].setdefault(host, [])
        data = (port, failure.getErrorMessage())
        hostData.append(data)

    def doReport(self, ignore):
        results = self.getSuccesses().items()
        if results:
            print "Open Ports:"
        else:
            print "No open ports found."
        for host, ports in results:
            print "\tHost: %s" % host
            for port in ports:
                print "\t\topen port: %i" % port
        errors = {}
        results = self.getFailures().items()
        for host, portAndError in results:
            for port, error in portAndError:
                errors.setdefault(error, 0)
                errors[error] += 1
        if results and (opts.verbose or opts.spew):
            print "\nErrors encountered, and their counts:"
            for error, count in errors.items():
                print "\t%s -- %i" % (error, count)

    def writeConfigs(self, result):
        reactor.stop()
        basePath = FilePath('etc/services/ping_tcp')
        if not basePath.exists():
            basePath.makedirs()
        results = self.getSuccesses().items()
        if results:
            print "Writing config files:"
        for host, ports in results:
            hostname = gethostbyaddr(host)[0]
            cfgFile = basePath.child('%s.conf' % hostname)
            if cfgFile.exists():
                continue
            print "\t%s ..." % cfgFile.path
            cfgFile.touch()
            fh = cfgFile.open('w')
            ports = ','.join([str(x) for x in ports])
            cfg = TCPPingServiceConfigTemplate % (host, ports)
            fh.write(cfg)
            fh.close()

    def getSuccesses(self):
        return self.data['success']

    def getFailures(self):
        return self.data['failure']


def main():
    nets = Networks([CIDR(x) for x in blocks])
    total = nets.getHostCount()
    netword = getSimplePlural('network', len(nets))
    hostword = getSimplePlural('host', total)
    countMsg = 'for a total of %s %s' % (total, hostword)
    print '\nBeginning scan on the following %s (%s):' % (netword, countMsg)
    for net in nets:
        print '\t%s' % net
    scanner = Scanner(nets.iterIPs(), ports, opts.batchSize, opts.timeout)
    scanner.run()


if __name__ == '__main__':
    main()
