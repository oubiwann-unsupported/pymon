import sys
sys.path.append('../')

import Monitor

########################
# Adytum Server 2 HTTP #
########################
mon = Monitor.Monitor(debug=1)
mon.remote_host = 'shell2.adytum.us'
mon.getRemoteProcessList()
mon.match_list  = [ 'http',     ]
mon.warn_thresh = [ 4,          ]
mon.err_thresh  = [ 12,         ]
mon.notification_list = [
  'duncan.mcgreggor@adytumsolutions.com',
]
mon.processMonitor()
