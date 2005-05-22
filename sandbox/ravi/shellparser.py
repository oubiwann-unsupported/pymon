from pyparsing import Word, Combine, Suppress, CharsNotIn, nums
from pyparsing import alphas, alphanums
from pyparsing import CaselessLiteral
from pyparsing import Optional
from pyparsing import Forward
import dispatch

class ShellParser:
    '''
    >>> p = ShellParser()
    >>> p.parse('show 192.168.0.1 http status')
    >>> print p.command()
    ('192.168.0.1', (['http'], {}), 'show', 'status')
    >>> p.parse('show 192.168.0.1 http config')
    >>> print p.command()
    ('192.168.0.1', (['http'], {}), 'show', 'config')
    >>> p.parse('show 192.168.0.1 * config')
    >>> print p.command()
    ('192.168.0.1', (['*'], {}), 'show', 'config')
    >>> p.parse('show * escalations')
    >>> p.command()
    ((['*'], {}), 'show', 'escalations')
    >>> p.parse('show 192.156.5.5 escalations')
    >>> p.command()
    ((['192.156.5.5'], {}), 'show', 'escalations')
    >>> p.parse('help')
    >>> p.command()
    ['help']
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

    [ command.when("self.cmd_type == 'help' or self.cmd_type == '?'") ]
    def commandHelp(self):
        cmd_list = ['help']
        return cmd_list

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
        cmd_pattern = Forward()
        cmd_pattern <<  ( cmd_start.setResultsName("cmd_action") \
            + ip_address.setResultsName("ip_addr") \
            + (monitor | "*").setResultsName("monitor") \
            + cmd_type.setResultsName("cmd_type") )
        tokens = cmd_pattern.parseString(self.cmd)
        ip_addr = tokens.ip_addr
        monitor = tokens.monitor
        cmd_action = tokens.cmd_action
        cmd_type = tokens.cmd_type
        return ip_addr, monitor, cmd_action, cmd_type


    [ command.when("self.cmd_type == 'config'") ]
    def commandConfig(self):
        integer = Word(nums)
        ip_address = Combine(integer + "." +
            integer + "." + integer + "." +
            integer)
        cmd_start = CaselessLiteral("show")
        cmd_type = CaselessLiteral("config")
        monitor = Word(alphas, alphanums)

        # parsing stuff
        cmd_pattern = Forward()
        cmd_pattern <<  ( cmd_start.setResultsName("cmd_action") \
            + ip_address.setResultsName("ip_addr") \
            + (monitor | "*").setResultsName("monitor") \
            + cmd_type.setResultsName("cmd_type") )
        tokens = cmd_pattern.parseString(self.cmd)
        ip_addr = tokens.ip_addr
        monitor = tokens.monitor
        cmd_action = tokens.cmd_action
        cmd_type = tokens.cmd_type
        return ip_addr, monitor, cmd_action, cmd_type

    [ command.when("self.cmd_type == 'escalations'") ]
    def commandConfig(self):
        integer = Word(nums)
        ip_address = Combine(integer + "." +
            integer + "." + integer + "." +
            integer)
        cmd_start = CaselessLiteral("show")
        cmd_type = CaselessLiteral("escalations")
        cmd_pattern = Forward()
        cmd_pattern <<  ( cmd_start.setResultsName("cmd_action") \
            + (ip_address | "*").setResultsName("ip_addr") \
            + cmd_type.setResultsName("cmd_type") )
        tokens = cmd_pattern.parseString(self.cmd)
        ip_addr = tokens.ip_addr
        cmd_action = tokens.cmd_action
        cmd_type = tokens.cmd_type
        return ip_addr, cmd_action, cmd_type

def _test():
    import doctest, shellparser
    doctest.testmod(shellparser)

if __name__ == '__main__':
    _test()
