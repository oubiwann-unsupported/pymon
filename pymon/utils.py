import re
import md5
import subprocess

import ZConfig

import simplejson

URI_REGEX = r'^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?'
URI_RE = re.compile(URI_REGEX)

# this regex doesn't work for just host or just host+port
AUTH_REGEX = r'^(([^:/?#@]+):)?(([^:/?#]+)@)?([^/?#:]*)(:([0-9]+))?'
AUTH_RE = re.compile(AUTH_REGEX)

class Uri(object):
    '''
    A convenience class for access parts of a URI as defined by 
    RFC 2396 (see http://www.faqs.org/rfcs/rfc2396.html).

    >>> u = Uri("ping://hostname")
    >>> u.getScheme()
    'ping'
    >>> u.getAuthority().getHost()
    'hostname'

    >>> u = Uri("http+status://hostname")
    >>> u.getScheme()
    'http+status'
    >>> u.getAuthority().getHost()
    'hostname'

    >>> u = Uri("remote+process://bind@hostname")
    >>> u.getScheme()
    'remote+process'
    >>> a = u.getAuthority()
    >>> a.getUser()
    'bind'
    >>> a.getHost()
    'hostname'
    >>> u.getPath()
    >>> u.getQuery()
    {}
    >>> u.getFragment()

    >>> u = Uri("http+scrape://hostname/page_name.html?string=Welcome+to+plone")
    >>> u.getScheme()
    'http+scrape'
    >>> a = u.getAuthority()
    >>> a.getHost()
    'hostname'
    >>> u.getPath()
    '/page_name.html'
    >>> q = u.getQuery()
    >>> q.string
    'Welcome+to+plone'

    >>> u = Uri("hostname/page_name.html?string=Welcome+to+plone")
    >>> u.getScheme()
    >>> a = u.getAuthority()
    >>> a.getHost()
    'hostname'
    >>> u.getPath()
    '/page_name.html'
    >>> q = u.getQuery()
    >>> q.string
    'Welcome+to+plone'

    '''
    def __init__(self, uri):
        self.uri = uri
        self.matches = URI_RE.match(uri)

    def getScheme(self):
        return self.matches.group(2)

    def getAuthority(self):
        return Authority(self.matches.group(4))

    def getPath(self):
        path = self.matches.group(5)
        if not path:
            return None
        return self.matches.group(5)

    def getQuery(self):
        return Query(self.matches.group(7))

    def getFragment(self):
        return self.matches.group(9)

class Authority(object):
    '''
    A custom URI Authority section parser.

    This section is parsed according to the spec for URLs in 
    RFC 1738, section 3.1 (http://www.faqs.org/rfcs/rfc1738.html):
        <user>:<password>@<host>:<port>/<url-path>

    >>> auth = 'oubiwann:secret@adytum.us:8080'
    >>> a1 = Authority(auth)
    >>> a1.getUser()
    'oubiwann'
    >>> a1.getPassword()
    'secret'
    >>> a1.getHost()
    'adytum.us'
    >>> a1.getPort()
    8080

    >>> auth = 'oubiwann@adytum.us:8080'
    >>> a2 = Authority(auth)
    >>> a2.getUser()
    'oubiwann'
    >>> a2.getPassword()
    >>> a2.getHost()
    'adytum.us'
    >>> a2.getPort()
    8080

    >>> auth = 'oubiwann@adytum.us'
    >>> a3 = Authority(auth)
    >>> a3.getUser()
    'oubiwann'
    >>> a3.getPassword()
    >>> a3.getHost()
    'adytum.us'
    >>> a3.getPort()

    >>> auth = 'adytum.us:8080'
    >>> a4 = Authority(auth)
    >>> a4.getUser()
    >>> a4.getPassword()
    >>> a4.getHost()
    'adytum.us'
    >>> a4.getPort()
    8080

    '''
    def __init__(self, auth):
        self.auth = auth
        auths = auth.split('@')
        if len(auths) == 2:
            userpass = auths.pop(0)
            userpass = userpass.split(':')
            self.user = userpass.pop(0)
            try:
                self.passwd = userpass.pop(0)
            except:
                self.passwd = None
        else:
            self.user = self.passwd = None
        hostport = auths[0].split(':')
        self.host = hostport.pop(0)
        try:
            self.port = hostport.pop(0)
        except:
            self.port = None
            

    def getUser(self):
        return self.user

    def getPassword(self):
        return self.passwd

    def getHost(self):
        return self.host

    def getPort(self):
        if self.port:
            return int(self.port)
        
class Query(dict):
    '''
    A custom URI Query section parser.
    
    >>> q = Query('state=ME&city=Bangor&st=Husson+Ave.&number=1320')
    >>> q['state']
    'ME'
    >>> q['number']
    '1320'
    >>> q['doesntexist']
    Traceback (most recent call last):
    KeyError: 'doesntexist'

    >>> q.state
    'ME'
    >>> q.number
    '1320'
    >>> q.doesntexist
    Traceback (most recent call last):
    AttributeError: 'Query' object has no attribute 'doesntexist'

    >>> q = Query('state=ME')
    >>> q.state
    'ME'
    '''
    def __init__(self, query):
        self.query = query
        if query:
            query_dict = dict([x.split('=') for x in query.split('&') ])
            self.update(query_dict)
            for key, val in query_dict.items():
                self.__setattr__(key, val)

class LocalTools:

  def getPasswdFromFile(self, filename):
    return file(filename).readline()

def getService(db_type):
    from pymon.api import storage
    return eval('storage.%s.Service' % db_type)

def updateDatabase(data):
    pass

def isInRange(datum, incl_range):
    minimum, maximum = incl_range.split(',')
    if int(minimum) <= int(datum) <= int(maximum):
        return True
    return False

def isInList(datum, in_list):
    '''
    >>> test_list = [200, 303, 304, 401]
    >>> isInList(200, test_list)
    True
    >>> isInList('200', test_list)
    True
    >>> isInList('405', test_list)
    False
    '''
    list = [ x.strip() for x in list_string.split(',') ]
    if str(datum) in list:
        return True
    return False

def makeUID(scheme, uri_remainder):
    return (('%s://%s') % (scheme, uri_remainder)).replace(' ', '+')

def getTypeFromURI(uri):
    # parse URI
    uri = Uri(uri)
    # get scheme
    scheme = uri.getScheme()
    return scheme.replace('+', ' ')

def getFriendlyTypeFromURI(uri):
    return getTypeFromURI(uri).replace('_', ' ')

def getHostFromURI(uri):
    return Uri(uri).getAuthority().getHost()

def _test():
    import doctest, utils
    return doctest.testmod(utils)

if __name__ == '__main__':
    _test()
