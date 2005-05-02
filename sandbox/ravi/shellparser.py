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
        """init method"""

    def parse(self, cmd):
        white_chars = " "
        self.cmd = cmd
        cmd_list = cmd.split(white_chars)
        self.cmd_type = cmd_list[-1]

    [ dispatch.generic() ]
    def command(self):
        """generic method for cmd"""

    [ command.when("self.cmd_type == 'status'") ]
    def commandStatus(self):
        # grammar stuff
        integer = Word(nums)
        ip_address = Combine(integer + "." +
            integer + "." + integer + "." +
            integer)
        cmd_start = CaselessLiteral("show")
        cmd_type = CaselessLiteral("status")
        monitor = Word(alphas, alphanums)

        # parsing stuff
        cmd_pattern =  cmd_start.setResultsName("cmd_action") \
            + ip_address.setResultsName("ip_addr") \
            + monitor.setResultsName("monitor") \
            + cmd_type.setResultsName("cmd_type")
        for srvr, startloc, endloc in cmd_pattern.scanString(self.cmd):
            ip_addr = srvr.ip_addr
            monitor = srvr.monitor
            cmd_action = srvr.cmd_action
            cmd_type = srvr.cmd_type
        return ip_addr, monitor, cmd_action, cmd_type

def _test():
    import doctest, shellparser
    doctest.testmod(shellparser)

if __name__ == '__main__':
    _test()
