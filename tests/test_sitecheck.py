import sys
sys.path.append('../')

import Monitor

########################
# Adytum Server 2 HTTP #
########################
mon = Monitor.Monitor(debug=True)
mon.titles = ['Google','Yahoo','SourceForge','W3C','Adytum','Adytum',]
mon.site_list  = [ 
  'http://google.com',
  'http://yahoo.com',
  'http://sf.net',
  'http://w3.org',
  'http://adytum.us',
  'http://adytumsolutions.com',
]
mon.warn_thresh = [ 8, 8, 8, 8, 8, 8,     ]
mon.err_thresh  = [ 5, 5, 5, 5, 5, 5,     ]
mon.notification_list = [
  'duncan.mcgreggor@adytumsolutions.com',
]
mon.webSiteMonitor()
