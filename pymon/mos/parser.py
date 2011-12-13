from grammar import Grammar


class ShellParser(object):

    services = None

    def __init__(self):
        self.tokens = None

    def __call__(self, command_string):
        self.parse(command_string)

    def buildGrammar(self):
        self.grammar = Grammar()
        self.grammar.parser = self
        self.grammar.makeBNF()
        return self.grammar

    def parse(self, cmd):
        tokens = grammar.parseString(cmd)
        out = """
            command: %s
            service type: %s
            action: %s
        """ % (tokens.commandtype, tokens.servicetype, tokens.action)
        self.tokens = tokens
        return out


def _test():
    import doctest, parser
    doctest.testmod(parser)


if __name__ == '__main__':
    _test()
