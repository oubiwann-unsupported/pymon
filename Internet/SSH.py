import pexpect
import getpass
import sys

#
# Some constants. These are regular expressions.
#
TERMINAL_PROMPT = 'Terminal type?'
TERMINAL_TYPE = 'vt100'
COMMAND_PROMPT = '[$#\>] ' ### This is way too simple for industrial use :-) ...
              # This is the prompt we get if SSH does not have 
              # the remote host's public key stored in the cache.
SSH_NEWKEY = 'Are you sure you want to continue connecting (yes/no)?'
PASSWORD_PROMPT_MYSQL = 'Enter password: '

class remoteCmd:

    def __init__(self, host, user, password=None):
        self.host = host
        self.user = user
        self.password = password
        self.debug = 1
        #
        # Login via SSH
        #
        cmd = '/usr/bin/ssh -l %s %s' % (user, host)
        if self.debug:
          print cmd
        self.child = pexpect.spawn(cmd)
        #i = self.child.expect([pexpect.TIMEOUT, SSH_NEWKEY, 'password: '])
        ##i = self.child.expect([TIMEOUT, SSH_NEWKEY, 'password: '])
        #if i == 0: # Timeout
        #        print 'ERROR!'
        #        print 'SSH could not login. Here is what SSH said:'
        #        print self.child.before, self.child.after
        #        sys.exit (1)
        #if i == 1: # SSH does not have the public key. Just accept it.
        #        self.child.sendline ('yes')
        #        self.child.expect ('password: ')
        #self.child.sendline(password)

            # Now we are either at the command prompt or
            # the login process is asking for our terminal type.
        i = self.child.expect ([COMMAND_PROMPT, TERMINAL_PROMPT])
        if i == 1:
                self.child.sendline (TERMINAL_TYPE)
                self.child.expect (COMMAND_PROMPT)

    def rexec(self, cmd, only_output=1):
        #
        # Now we should be at the command prompt and ready to run some commands.
        #
        self.child.sendline (cmd)
        self.child.expect (COMMAND_PROMPT)
        #output = self.child.before.split('\n')
        return self.child.before
        if only_output:
            return output[1]
        else:
            return output

    def close(self):
        # Now exit the remote host.
        self.child.sendline ('exit')
        self.child.expect(pexpect.EOF)

class remoteCopy:

    def __init__(self):
        self.srchost = ''
        self.srcuser = ''
        self.srcdir = ''
        self.dsthost = ''
        self.dstuser = '' 
        self.dstdir = ''
        self.password = ''


    def copy(self):
        source = ''
        dest = ''
        if self.srchost and self.srcuser:
          source = '%s@%s:' % (self.srcuser, self.srchost)
        if self.dsthost and self.dstuser:
          dest = '%s@%s:' % (self.dstuser, self.dsthost)
        self.cmd = '/usr/bin/scp %s%s %s%s'%(source, self.srcdir, dest, self.dstdir)
        self.child = pexpect.spawn(self.cmd)
        i = self.child.expect([pexpect.TIMEOUT, SSH_NEWKEY, 'Password: '])
        if i == 0: # Timeout
                print 'ERROR!'
                print 'SSH could not login. Here is what SSH said:'
                print self.child.before, self.child.after
                sys.exit (1)
        if i == 1: # SSH does not have the public key. Just accept it.
                self.child.sendline ('yes')
                self.child.expect ('Password: ')
        self.child.sendline(self.password)
        self.child.sendline ('\r\n')
        print self.child.before, self.child.after
