from twisted.web.client import HTTPPageGetter, HTTPClientFactory, PartialDownloadError
from twisted.web.http import HTTPClient

from base import ClientMixin

class HttpTextClient:

    def connectionLost(self, reason):
        pass
    
class HttpStatusClient(HTTPPageGetter):
    
    def connectionLost(self, reason):
        status = self.factory.status
        host = self.factory.uid
        print "Status: %s for %s" % (status, host)
