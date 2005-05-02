from pyparsing import Word, Combine, Suppress, CharsNotIn, nums
from pyparsing import alphas, alphanums
from pyparsing import CaselessLiteral
import dispatch

class ShellParser:
    '''
    >>> p = ShellParser(
    >>> p.parse('show 192.168.0.1 http status')
    >>> print p.command()
    '''

    def __init__(self):
        self.ip_addr = "";
        self.monitor = "";
        self.cmd_action = "";
        self.cmd_type = "";

    def parse(self, cmd):
        integer = Word(nums)
        ip_address = Combine( integer + "." + integer + "." + integer + "." + integer )
        cmd_start = CaselessLiteral("show")
        cmd_type = CaselessLiteral("status")
        monitor = Word( alphas, alphanums)
        cmd_pattern =  cmdStart.setResultsName("cmdAction") + ipAddress.setResultsName("ipAddr") + monitor.setResultsName("monitor") + cmdType.setResultsName("cmdType")
        parsed_tuple = cmdPattern.scanString(cmd)

        for srvr, startloc, endloc in parsed_tuple:
            self.ip_addr = srvr.ip_addr
            self.monitor = srvr.monitor
            self.cmd_action = srvr.cmd_action
            self.cmd_type = srvr.cmd_type

    [dispatch.generic()]
    def command(self):
        """generic method for cmd"""

    [command.when("self.cmd_type == 'status'")]
    def commandStatus(self):
        return self.ip_addr, self.monitor, self.cmd_action, self.cmd_type

def _test():
    import doctest, parser
    doctest.testmod(parser)

if __name__ == '__main__':
    _test()
