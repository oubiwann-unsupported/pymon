from pyparsing import Word, Combine, Suppress, CharsNotIn
from pyparsing import Group, Optional, ZeroOrMore
from pyparsing import nums, alphas, alphanums, oneOf
from pyparsing import Literal, CaselessLiteral, Forward

from pymon.zconfig import getDateRange


legalPathChars = Word(alphanums + "~/_-().?,;")


def getDateRange(orig, location, tokens):
    key = tokens.keys()[0]
    date = getDateRange(tokens[key])
    return [date]


def makeInt(orig, location, tokens):
    key = tokens.keys()[0]
    return int(tokens[key])


class Grammar(object):
    '''
    # setup the ShellParser and set the services; in a real application,
    # this will be done at a higher level (where configuration is in its
    # proper place).
    >>> p = ShellParser()
    >>> p.services = ['ping', 'http-status']
    >>> grammar = p.buildGrammar()
    >>> g = grammar.bnf

    # test help token
    >>> tokens = g.parseString("help")
    >>> tokens.commandtype
    'help'

    # test some show tokens
    >>> tokens = g.parseString("show nodes")
    >>> tokens.action
    'nodes'
    >>> tokens = g.parseString("show services")
    >>> tokens.action
    'services'
    >>> tokens = g.parseString("show lists")
    >>> tokens.action
    'lists'

    # test a basic node token
    >>> tokens = g.parseString("node add www1_anon_user www.adytum.us")
    >>> tokens.commandtype
    'node'
    >>> tokens.name
    'www1_anon_user'
    >>> tokens.action
    'add'
    >>> tokens.uri
    'www.adytum.us'

    # test with more complicated uri
    >>> tokens = g.parseString("node add www1_auth_user pymonuser:asecret@www.adytum.us")
    >>> tokens.name
    'www1_auth_user'
    >>> tokens.uri
    'pymonuser:asecret@www.adytum.us'

    # let's show a particular node
    >>> tokens = g.parseString("node show www1_auth_user")
    >>> tokens.action
    'show'
    >>> tokens.name
    'www1_auth_user'

    # test a node token with lots in it
    >>> tokens = g.parseString("service http-status add www1_anon_user path /test/index.html")
    >>> tokens.commandtype
    'service'
    >>> tokens.servicetype
    'http-status'
    >>> tokens.action
    'add'
    >>> tokens.name
    'www1_anon_user'
    >>> tokens.path
    '/test/index.html'

    >>> tokens = g.parseString("service ping add www1_auth_user enabled True org Adytum interval 20 binary /here/ping count 10 ok-threshold dummyokthresh warn-threshold dummywarnthresh error-threshold dummyerrorthresh failed-threshold dummyfailedthresh scheduled-downtime 2005.12.01 03:00:00 - 2005.12.01 04:00:00")
    >>> tokens.commandtype
    'service'
    >>> tokens.servicetype
    'ping'
    >>> tokens.action
    'add'
    >>> tokens.enabled
    'true'
    >>> tokens.org
    'Adytum'
    >>> tokens.interval
    20
    >>> tokens.binary
    '/here/ping'
    >>> tokens.count
    10

    >>> tokens.ok_threshold
    'dummyokthresh'
    >>> tokens.warn_threshold
    'dummywarnthresh'
    >>> tokens.error_threshold
    'dummyerrorthresh'
    >>> tokens.failed_threshold
    'dummyfailedthresh'
    >>> down = tokens.scheduled_downtime
    >>> print down['start']
    2005-12-01 03:00:00
    >>> print down['end']
    2005-12-01 04:00:00

    '''
    parser = None

    def __init__(self):
        self.bnf = None

    def makeBNF(self):
        # initial commands
        nodeToken = Literal("node").setResultsName(
            "commandtype")
        showToken = Literal("show").setResultsName(
            "commandtype")
        serviceToken = Literal("service").setResultsName(
            "commandtype")
        listToken = Literal("list").setResultsName(
            "commandtype")
        memToken = Literal("mem").setResultsName(
            "commandtype")
        helpToken = Literal("help").setResultsName(
            "commandtype")

        # XXX in the future, service types will be taken from the
        # configuration file... but not directly. Need to provide an
        # attribute so that higher up in the "chain" (at the factory
        # level?) the configuration data that the grammar needs can
        # be set. We'll look at protocol/factory attributes for
        # twisted factories and clients, respectively.
        svcs = ' '.join(self.parser.services)
        #svcs = 'testing ping http-status'
        serviceTypesToken = Optional(
            oneOf(
            svcs).setResultsName(
            "servicetype"))

        # commands
        serviceNodeActionsToken = oneOf(
            "add del delete update replace append").setResultsName(
            "action")
        serviceNodeShowActionToken = Literal(
            "show").setResultsName(
            "action")
        memActionsToken = oneOf(
            "write clear").setResultsName(
            "action")
        showActionsToken = oneOf(
            "nodes services lists").setResultsName(
            "action")

        # node args
        nodeNameToken = Word(alphanums + '_').setResultsName(
            "name")
        nodeUriToken = Word(alphanums + '/:@_-.').setResultsName(
            "uri")

        # general service args
        true = CaselessLiteral("true")
        false = CaselessLiteral("false")
        enabledToken = Optional(
            Literal("enabled") +
            (true | false).setResultsName(
            "enabled"))
        orgToken = Optional(
            Literal("org") +
            Word(alphanums + """.'",:;!?()@#$%&*<>/\\""").setResultsName(
            "org"))
        intervalToken = Optional(
            Literal("interval") +
            Word(nums).setParseAction(makeInt).setResultsName(
            "interval"))

        okThreshToken = Optional(
            Literal("ok-threshold") +
            Word(alphanums).setResultsName(
            "ok_threshold"))
        warnThreshToken = Optional(
            Literal("warn-threshold") +
            Word(alphanums).setResultsName(
            "warn_threshold"))
        errorThreshToken = Optional(
            Literal("error-threshold") +
            Word(alphanums).setResultsName(
            "error_threshold"))
        failedThreshToken = Optional(
            Literal("failed-threshold") +
            Word(alphanums).setResultsName(
            "failed_threshold"))
        thresholdsToken = okThreshToken + warnThreshToken + \
            errorThreshToken + failedThreshToken

        downtimeToken = Optional(
            Literal("scheduled-downtime") +
            Word(
                nums + "." + " " + nums + ":" + " - " +
                nums + "." + " " + nums + ":"
            ).setParseAction(getDateRange).setResultsName(
            "scheduled_downtime"))

        # ping-specific args
        pingBinaryToken = Optional(
            Literal("binary") +
            legalPathChars.setResultsName(
            "binary"))
        pingCountToken = Optional(
            Literal("count") +
            Word(nums).setParseAction(makeInt).setResultsName(
            "count"))

        pingArgs = Optional(pingBinaryToken + pingCountToken)

        # http-specifc args
        pathToken = Optional(
            Literal("path") +
            Word(alphanums + "/-_+?#.,~@").setResultsName(
            "path"))

        # assembled node grammar
        fullNodeNoShow = serviceNodeActionsToken + \
            nodeNameToken + nodeUriToken + enabledToken + orgToken + \
            intervalToken + downtimeToken
        fullNodeShow = serviceNodeShowActionToken + nodeNameToken
        fullNodeToken = nodeToken + (fullNodeNoShow | fullNodeShow)

        # assembled show grammar
        fullShowToken = showToken + showActionsToken

        # assembled service grammar
        fullServiceToken = serviceToken + serviceTypesToken + \
            serviceNodeActionsToken + nodeNameToken + pathToken + \
            enabledToken + orgToken + intervalToken + pingArgs + \
            thresholdsToken + downtimeToken

        # assembled notification-list grammar
        fullListToken = listToken

        # assembled mem grammar
        fullMemToken = memToken + memActionsToken

        # assembled help grammar
        fullHelpToken = helpToken

        # complete grammar
        command = (fullNodeToken | fullShowToken | fullServiceToken |
            fullListToken | fullMemToken | fullHelpToken)

        self.bnf = command


def _test():
    import doctest, grammar
    doctest.testmod(grammar)


if __name__ == '__main__':
    _test()
