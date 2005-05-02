from pyparsing import Word, Combine, Suppress, CharsNotIn, nums
from pyparsing import alphas, alphanums
from pyparsing import CaselessLiteral
import dispatch

class ShellParser:
    '''
    >>> p = ShellParser()
    >>> p.parse('show 192.168.0.1 http status')
    >>> print p.command()
    ('192.168.0.1', 'http', 'show', 'status')
    '''

    def __init__(self):
        self.ip_addr = "";
        self.monitor = "";
        self.cmd_action = "";
        self.cmd_type = "";

    def parse(self, cmd):
        # grammar stuff
        integer = Word(nums)
        ip_address = Combine(integer + "." + integer + "." + integer + "." + integer)
        cmd_start = CaselessLiteral("show")
        cmd_type = CaselessLiteral("status")
        monitor = Word(alphas, alphanums)

        # parsing stuff
        cmd_pattern =  cmd_start.setResultsName("cmd_action") + ip_address.setResultsName("ip_addr") + monitor.setResultsName("monitor") + cmd_type.setResultsName("cmd_type")
        for srvr, startloc, endloc in cmd_pattern.scanString(cmd):
            self.ip_addr = srvr.ip_addr
            self.monitor = srvr.monitor
            self.cmd_action = srvr.cmd_action
            self.cmd_type = srvr.cmd_type

    [ dispatch.generic() ]
    def command(self):
        """generic method for cmd"""

    [ command.when("self.cmd_type == 'status'") ]
    def commandStatus(self):
        return self.ip_addr, self.monitor, self.cmd_action, self.cmd_type

def _test():
    import doctest, shellparser
    doctest.testmod(shellparser)

if __name__ == '__main__':
    _test()
