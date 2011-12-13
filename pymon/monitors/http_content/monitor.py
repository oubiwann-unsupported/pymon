from twisted.web.client import HTTPClientFactory

from pymon.monitors.base import BaseMonitor


class HttpTextMonitor(HTTPClientFactory, BaseMonitor):

    def __init__(self, uid):
        BaseMonitor.__init__(self, uid, cfg)
        self.page_url = ''
        self.text_check = ''
        self.checkdata = self.service.entries.entry(uri=self.uid)
