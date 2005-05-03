from datetime import datetime

from twisted.protocols import telnet
from twisted.internet import protocol
from twisted.internet import defer
from twisted.internet import reactor
from twisted.python import log
from twisted.cred import credentials
from twisted.cred import checkers
from twisted.cred.error import UnauthorizedLogin
from twisted.python import components

from zope import interface
from zope.interface import Interface, implements

#from imagination.text import english
#from imagination import errors

import interfaces
import shellparser
import version

DEBUG = 0
WONTECHO = ''.join((telnet.IAC, telnet.WONT, telnet.ECHO))
WILLECHO = ''.join((telnet.IAC, telnet.WILL, telnet.ECHO))

class NoSelection(Exception):
    pass

class ShellServer(telnet.Telnet):
    mode = "Username"

    # XXX
    implements(interfaces.IUI)

    needsPrompt = True

    def send(self, text):
        self.write(text)

    def block(self, deferred):
        self.mode = "Blocked"
        deferred.addBoth(self._unblock)
        return deferred

    def _unblock(self, resultOrFailure):
        self.mode = None
        return resultOrFailure

    def telnet_Blocked(self, line):
        self.send("Please wait...\r\n")

    def connectMessage(self):
        """A message welcoming you to the server.

        This should return a string which will be displayed to every user
        when they initially connect.
        """
        return '\nWelcome to %s %s (%s).\n\n' % (version.name, 
            version.number, version.codename)

    def connectionMade(self):
        self.send(self.connectMessage())
        self.send("Username: ")

    '''
    def telnet_Username(self, username):
        # XXX
        #self.avatar = self.factory.actorTemplate[
        #    interfaces.IUI: lambda x: self].fill(
        #    english.INoun, name=username).new()
        #self.userLoggedIn()
        return "Command"
    '''
    def telnet_Username(self, username):
        self.userLoggedIn()
        return "Command"
        #return "Password"

    def telnet_Password(self, password):
        pass

    def welcomeMessage(self):
        '''
        return ''.join((
            "\r\nTR: connected to ",
            # XXX
            english.INoun(self.avatar).name,
            '\r\n'
        ))
        '''
        return '(Replace with custom welcome message)\n'

    def userLoggedIn(self):
        self.send(self.welcomeMessage())
        #self.telnet_Command("look")
        #self.telnet_Command("help")
        self.send(self.commandPrompt())

    def telnet_Command(self, cmd):
        self.needsPrompt = True
        # XXX
        #d = defer.maybeDeferred(english.IThinker(self.avatar).parse, cmd)
        parser = shellparser.ShellParser()
        parser.parse(cmd)
        d = defer.maybeDeferred(parser.command)
        d.addErrback(self._ebParsed)
        d.addCallback(self._cbParsed)

    def _ebParsed(self, failure):
        # XXX
        #if failure.check(errors.RealityException):
            # XXX
        #    self.send(english.express(failure.value, self.avatar) + '\r\n')
        #else:
        #    self.send("Internal parse error: %s\r\n" % (failure.value,))
        #    return failure
        msg = 'There seems to have been a problem...\n%s' % str(failure)
        return msg

    def _cbParsed(self, result):
        self.send(self.subCommandPrompt())
        self.send(result + '\n')
        self.send(self.commandPrompt())
        self.needsPrompt = False

    def basePrompt(self):
        timestamp = datetime.now().strftime('%H:%M:%S')
        return '%s:%s %s' % (self.factory.hostname, 
            self.factory.instancename, timestamp)

    def commandPrompt(self):
        # XXX add logic here for determing what level/subshell
        # we are in
        #return english.express(self.avatar, self.avatar) + '> '
        return '%s > ' % (self.basePrompt())

    def subCommandPrompt(self):
        return '%s . ' % (self.basePrompt())

    # IUI implementation
    def presentEvent(self, eventInterface, event):
        # XXX
        #s = english.express(event, self.avatar) + "\r\n"
        s = 'english.express ' + "\r\n"
        if not self.needsPrompt:
            s = "\r\n" + s
        self.send(s)

    choiceDeferred = choiceItems = None

    def presentMenu(self, items, typename=None):
        if self.choiceDeferred is not None:
            self.choiceDeferred.errback(NoSelection())
        self.choiceDeferred = None

        lines = []
        if typename is not None:
            lines.append("Which %s do you mean?" % (typename,))
        for i in items:
            # XXX
            lines.append("%d. %s" % (len(lines), english.express(i, self.avatar)))
        lines.append('Choose: ')
        self.send('\r\n'.join(lines))
        self.mode = "Choosing"
        self.choiceDeferred = defer.Deferred().addErrback(self._ebChoice)
        self.choiceItems = items
        return self.choiceDeferred

    def _ebChoice(self, failure):
        if not failure.check(NoSelection):
            self.send("Internal menu error: %s\r\n" % (failure.value,))
        return failure

    def telnet_Choosing(self, text):
        try:
            val = int(text)
        except ValueError:
            self.mode = "Command"
            return self.telnet_Command(text)
        else:
            if val < 1 or val > len(self.choiceItems):
                self.send("Try again: ")
            else:
                self.mode = "Command"
                d, self.choiceDeferred = self.choiceDeferred, None
                d.callback(val - 1)


class ShellFactory(protocol.ServerFactory):
    #def __init__(self, actorTemplate):
    #    self.actorTemplate = actorTemplate
    def __init__(self, hostname='', instancename=''):
        self.hostname = hostname
        self.instancename = instancename

    protocol = ShellServer
