from twisted.web.client import HTTPPageGetter, HTTPClientFactory, PartialDownloadError
from twisted.web.http import HTTPClient

from base import ClientMixin

class HttpTextClient:

    def connectionLost(self, reason):
        pass
    
class HttpStatusClient(HTTPPageGetter, ClientMixin):
    
    def connectionLost(self, reason):
        status = self.factory.status
        host = self.getHost()
        print "Status: %s for %s" % (status, host)
