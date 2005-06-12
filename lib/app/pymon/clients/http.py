from twisted.web.client import HTTPPageGetter, HTTPClientFactory, PartialDownloadError

from base import ClientMixin

class HttpTextClient:

    def connectionLost(self, reason):
        pass
    
class HttpStatusClient:
    
    def connectionLost(self, reason):
        status = self.factory.status
