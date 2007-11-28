import re

XMIT = 0
XCVD = 1
LOSS = 2
TIME = 3

IPHOST_LINE = 0
LOSS_LINE = -2
AVE_LINE = -1

MAC_TESTDATA = ''' PING google.com (216.239.57.99): 56 data bytes
64 bytes from 216.239.57.99: icmp_seq=0 ttl=240 time=111.108 ms
64 bytes from 216.239.57.99: icmp_seq=1 ttl=240 time=104.348 ms
64 bytes from 216.239.57.99: icmp_seq=2 ttl=240 time=99.88 ms
64 bytes from 216.239.57.99: icmp_seq=3 ttl=240 time=103.395 ms

--- google.com ping statistics ---
4 packets transmitted, 3 packets received, 25% packet loss
round-trip min/avg/max = 99.88/104.682/111.108 ms
'''

LNX_TESTDATA = ''' PING google.com (216.239.57.99) 56(84) bytes of data.
64 bytes from 216.239.57.99: icmp_seq=1 ttl=241 time=88.7 ms
64 bytes from 216.239.57.99: icmp_seq=2 ttl=241 time=89.1 ms
64 bytes from 216.239.57.99: icmp_seq=3 ttl=241 time=89.2 ms
64 bytes from 216.239.57.99: icmp_seq=4 ttl=241 time=88.9 ms

--- google.com ping statistics ---
4 packets transmitted, 2 received, 50% packet loss, time 9300ms
rtt min/avg/max/mdev = 88.745/89.046/89.265/0.290 ms
'''

FLL_TESTDATA = ''' PING google.com (216.239.57.99) 56(84) bytes of data.
64 bytes from 216.239.57.99: icmp_seq=1 ttl=241 time=88.7 ms
64 bytes from 216.239.57.99: icmp_seq=2 ttl=241 time=89.1 ms
64 bytes from 216.239.57.99: icmp_seq=3 ttl=241 time=89.2 ms
64 bytes from 216.239.57.99: icmp_seq=4 ttl=241 time=88.9 ms

--- google.com ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 9300ms
rtt min/avg/max/mdev = 88.745/89.046/89.265/0.290 ms
'''


BAD_TESTDATA = ''' PING www.divorce-md.com (67.94.174.12): 56 data bytes

--- www.divorce-md.com ping statistics ---
3 packets transmitted, 0 packets received, 100% packet loss
'''

class OutputParser(object):
    '''
    # test instantiation
    >>> mac = OutputParser(MAC_TESTDATA)
    >>> lnx = OutputParser(LNX_TESTDATA)
    >>> fll = OutputParser(FLL_TESTDATA)
    >>> bad = OutputParser(BAD_TESTDATA)

    # test hostnames
    >>> mac.getHostname()
    'google.com'
    >>> lnx.getHostname()
    'google.com'
    >>> fll.getHostname()
    'google.com'
    >>> bad.getHostname()
    'www.divorce-md.com'

    # test lines
    >>> type(mac.pingLines())
    <type 'list'>
    >>> type(lnx.pingLines())
    <type 'list'>
    >>> type(fll.pingLines())
    <type 'list'>
    >>> type(bad.pingLines())
    <type 'list'>

    # test loss line
    >>> mac.getPingLossLine()
    '4 packets transmitted, 3 packets received, 25% packet loss'
    >>> lnx.getPingLossLine()
    '4 packets transmitted, 2 received, 50% packet loss, time 9300ms'
    >>> fll.getPingLossLine()
    '4 packets transmitted, 4 received, 0% packet loss, time 9300ms'
    >>> bad.getPingLossLine()

    # test peak line
    >>> mac.getPingPeakLine()
    'round-trip min/avg/max = 99.88/104.682/111.108 ms'
    >>> lnx.getPingPeakLine()
    'rtt min/avg/max/mdev = 88.745/89.046/89.265/0.290 ms'
    >>> fll.getPingPeakLine()
    'rtt min/avg/max/mdev = 88.745/89.046/89.265/0.290 ms'
    >>> bad.getPingPeakLine()

    # test packet counts 
    >>> mac.getPacketsXmit()
    '4 packets transmitted'
    >>> lnx.getPacketsXmit()
    '4 packets transmitted'
    >>> bad.getPacketsXmit()

    >>> mac.getPacketsXcvd()
    '3 packets received'
    >>> lnx.getPacketsXcvd()
    '2 received'
    >>> bad.getPacketsXcvd()

    # test packet loss
    >>> mac.getPingLoss()
    25
    >>> lnx.getPingLoss()
    50
    >>> fll.getPingLoss()
    0
    >>> bad.getPingLoss()
    100

    # test packet gain
    >>> mac.getPingGain()
    75
    >>> lnx.getPingGain()
    50
    >>> fll.getPingGain()
    100
    >>> bad.getPingGain()
    0

    # test min/max/ave data
    >>> res = mac.getPeakData().items()
    >>> res.sort()
    >>> res
    [('avg', '104.682'), ('max', '111.108'), ('min', '99.88')]
    >>> res = lnx.getPeakData().items()
    >>> res.sort()
    >>> res
    [('avg', '89.046'), ('max', '89.265'), ('mdev', '0.290'), ('min', '88.745')]
    >>> res = bad.getPeakData().items()
    >>> res.sort()
    >>> res
    []

  
    '''

    def __init__(self, ping_data):
        self.data = ping_data

    def getHostname(self):
        try:
            line = self.pingLines()[IPHOST_LINE]
            return line.split(' ')[1]
        except:
            pass

    def getHostIp(self):
        pass

    def pingLines(self):

        return self.data.splitlines()

    def getPingLossLine(self):

        try:
            line = self.pingLines()[LOSS_LINE]
            if re.match('.*%.*', line):
                return line
        except:
            pass

    def getPingPeakLine(self):

        try:
            line = self.pingLines()[AVE_LINE]
            if re.match('.*avg.*', line):
                return line
        except:
            pass

    def getPacketsXmit(self):

        line = self.getPingLossLine()
        if line:
            xmit = line.split(',')[XMIT].strip()
            if xmit:
                return xmit

    def getPacketsXcvd(self):

        line = self.getPingLossLine()
        if line:
            xcvd = line.split(',')[XCVD].strip()
            if xcvd:
                return xcvd

    def getPingLoss(self):
        '''
        this returns a percentage, the percentage packet loss
        from the ping command run against the host
        '''
        
        line = self.getPingLossLine()
        if line:
            parts = line.split(',')
            loss = int(parts[LOSS].split('%')[0].strip())
            if loss or loss == 0:
                return loss
        return 100

    def getPingGain(self):
        ''' 
        get the ping counts for each host, where the counts show how
        good the network connection is to the host by subtracting the
        percent loss from 100%.
        '''
        
        return 100 - self.getPingLoss()

    def getPeakData(self):
        line =  self.getPingPeakLine()
        if line:
            parts = self.getPingPeakLine().split(' ')
            EQUALS = parts.index('=')
            WORDS = EQUALS - 1
            NUMS = EQUALS + 1

            return dict(zip(parts[WORDS].split('/'), parts[NUMS].split('/')))
        else:
            return {}

def _test():
    import doctest, ping
    return doctest.testmod(ping)

if __name__ == '__main__':
    _test()

