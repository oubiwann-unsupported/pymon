import httplib
import urlparse

class Site:

  def _getUrlParts(self, siteurl=None):
    '''
    Get the parts of the URL.
    '''
    self.siteurl = siteurl
    url_tuple = urlparse.urlsplit(self.siteurl)
    if self.debug:
      print url_tuple
    self._proto = url_tuple[0]
    try:
      site = url_tuple[1].split(':')[0]
      port = url_tuple[1].split(':')[1]
    except:
      site = url_tuple[1]
      port = 0
    self._port = int(port)
    self._query = url_tuple[3]
    if self._query:
      self._path = '%s?%s' % (url_tuple[2], url_tuple[3])
    else:
      self._path = url_tuple[2]
    if not self._path:
      self._path = '/'
    self._site = site
    if self.debug:
      print self._path

class Web(Site):

  def __init__(self, siteurl=None, debug=0):
    '''
    init
    '''
    self.debug = debug
    self.httpconn = None
    self.httpresponse = None
    self.httpnormal = None


  def _httpConnect(self):
    '''
    Connect to web site that you want to
    monitor.
    '''
    if not self._port:
      self._port = 80
    self.httpconn = httplib.HTTPConnection('%s:%d' % (self._site, self._port))

  def _getHttpResponse(self):
    '''
    Get send a GET for a path to the site.
    '''
    if self.debug:
      print self._path
    self.httpconn.request("GET", self._path)
    self.httpresponse = self.httpconn.getresponse()
    self.httpconn.close()

    return (self.httpresponse.status, self.httpresponse.reason)

  def _normalizeHttpStatus(self):
    '''
    We need a way to assign HTTP return states to sequential
    values so that WARN and ERR thresholds are meaningful and
    useful.

    The values that we use are arbitrary: the higher the number,
    the better; WARN on middle numbers, ERR on low numbers. We
    have split the values across a range of 10:

      1-4: ERR
      5-7: WARN
      8-10: OK
    '''

    if not self.httpresponse:
      self._getHttpResponse()
    code = self.httpresponse.status
    msg = self.httpresponse.reason

    if self.debug:
      print code
      print msg

    # OK
    if code == 100:
      status = 8
    elif code == 101:
      status = 8
    elif code == 200:
      status = 10
    elif code == 201:
      status = 10
    elif code == 202:
      status = 9
    elif code == 203:
      status = 9
    elif code == 205:
      status = 9
    elif code == 206:
      status = 9
    elif code == 300:
      status = 9
    elif code == 302:
      status = 9
    elif code == 304:
      status = 9
    # WARN
    elif code == 301:
      status = 7
    elif code == 303:
      status = 7
    elif code == 204:
      status = 6
    elif code == 305:
      status = 7
    elif code == 307:
      status = 7
    elif code == 401:
      status = 5
    elif code == 403:
      status = 5
    # ERR
    elif code == 400:
      status = 2
    elif code == 404:
      status = 4
    elif code == 405:
      status = 4
    elif code == 406:
      status = 3
    elif code == 408:
      status = 3
    elif code == 409:
      status = 3
    elif code == 410:
      status = 3
    elif code == 500:
      status = 1
    elif code == 502:
      status = 1
    elif code == 503:
      status = 1
    elif code == 504:
      status = 3
    else:
      status = 0
    
    return (status, msg)
        
  def checkWebSite(self, siteurl=None):
    '''
    check site
    '''
    if self.debug:
      print siteurl
    self._getUrlParts(siteurl=siteurl)
    self._httpConnect()
    self._getHttpResponse()
    if self.debug:
      print self._normalizeHttpStatus()

    return self.httpresponse.status

  def getWebSiteCodes(self):
    ''' 
    get the http status codes for each web site and return
    both the message and the 
    '''
    status_codes = []
    if self.debug:
      print self.site_list
    for site in self.site_list:
        if self.debug:
          print site
        self.http = Web(siteurl=site, debug=self.debug)
        try:
          check = int(self.http.checkWebSite(site))
        except:
          check = 0
        status_codes.append(check)

    return status_codes
