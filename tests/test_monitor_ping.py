import sys
sys.path.append('../')
import Monitor

##############
# Ping Hosts #
##############
mon = Monitoring.Monitoring()
mon.host_list   = [
  'dns2.adytum.us',
  'mail2.adytum.us',
  'www2.adytum.us',
  'shell2.adytum.us',
  'www.adytum.us',
]
mon.warn_thresh  = [ 75,75,75,75,75 ]
mon.err_thresh = [ 50,50,50,50,50 ]
mon.notification_list = [
  'duncan.mcgreggor@adytumsolutions.com',
]
mon.hostsPingMonitor()

