'''
Monitors
========
protocol
__init__()
__repr__()
__call__()
call()
getStatus()

_setupNullClient()

clientConnectionFailed()
clientConnectionLost()

Monitor Mixin
-------------
Instead of monitor mixins, what about adaptors?

from zope.interface import Interface
from zope.interface import implements
from twisted.python.components import Componentized
from twisted.python.components import registerAdapter

from twisted.web.client import HTTPClientFactory
from twisted.web.http import HTTPClient

class IMonitor(Interface):
    pass

class IHTTPStatusMonitor(IMonitor):
    pass

class Monitor(Componentized):
    """
    Does all the stuff the mixin used to
    """
    implements(IMonitor)
    protocol = None

class HTTPStatusMonitor(HTTPClientFactory):
    implements(IHTTPStatusMonitor)
    protocol = HTTPClient

# this registers the HTTPStatusMonitor class (an adapter)
# it does so for ALL instances of the HTTPStatusMonitor class
registerAdapter(HTTPStatusMonitor, Monitor, IHTTPStatusMonitor)

Configuration
=============
* create IConfiguration
* 

Service Configuration Object
----------------------------
getUID()
getServiceType()
getService()


'''
