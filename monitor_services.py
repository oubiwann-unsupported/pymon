import Monitor

#################################
# Zope and Apache notifications #
#################################
mon = Monitor.Monitor()
# get currently running processes
mon.getProcessList()
# warning and error message thresholds. any process counts lower
# than the threshold will result in a message for that monitoring
# level
mon.titles      = [ 'Apache',    'Zope2.6',     'Zope2.7']
mon.match_list  = [ 'httpd',    'zopeuser',     'zope27']
mon.warn_thresh = [ 0,          2,              2,      ]
mon.err_thresh  = [ 1,          1,              1,      ]
mon.notification_list = [
  'duncan.mcgreggor@adytumsolutions.com',
]
mon.processMonitor()

####################################
# qmail pop3d and smtpd Monitoring #
####################################
mon = Monitor.Monitor(debug=False)
mon.getProcessList()
mon.titles      = [ 'SMTP', 'POP',  ]
mon.match_list  = [ 'qmail-smtpd',          'qmail-pop3d',  ]
mon.warn_thresh = [ 0,                      0,              ]
mon.err_thresh  = [ 2,                      2,              ]
mon.notification_list = [
  'duncan.mcgreggor@adytumsolutions.com',
  #'anthony.bollino@adytumsolutions.com',
]
mon.processMonitor()

###################################
# MySQL and PostgreSQL Monitoring #
###################################
mon = Monitor.Monitor()
mon.getProcessList()
mon.match_list  = [ 'mysql',    'pgsql',        ]
mon.warn_thresh = [ 4,          3,              ]
mon.err_thresh  = [ 1,          1,              ]
mon.notification_list = [
  'duncan.mcgreggor@adytumsolutions.com',
  #'anthony.bollino@adytumsolutions.com',
]
mon.processMonitor()

##################
# DNS Monitoring #
##################
mon = Monitor.Monitor(debug=False)
mon.getProcessList()
mon.match_list  = [ 'dns',  ]
mon.warn_thresh = [ 0,      ]
mon.err_thresh  = [ 4,      ]
mon.notification_list = [
  'duncan.mcgreggor@adytumsolutions.com',
]
mon.processMonitor()

###########
# NetMUSH #
###########
mon = Monitor.Monitor()
mon.getProcessList()
mon.match_list  = [ 'netmush',  ]
mon.warn_thresh = [ 0,          ]
mon.err_thresh  = [ 1,          ]
mon.notification_list = [
  'duncan.mcgreggor@adytumsolutions.com',
]
mon.processMonitor()

####################
# ZopeCRM Maildrop #
####################
mon = Monitor.Monitor()
mon.getProcessList()
mon.titles      = [ 'MaildropHost Daemon',  ]
mon.match_list  = [ 'maildrop.py',  ]
mon.warn_thresh = [ 0,          ]
mon.err_thresh  = [ 1,          ]
mon.notification_list = [
  'duncan.mcgreggor@adytumsolutions.com',
]
mon.processMonitor()

##############
# Ping Hosts #
##############
mon = Monitor.Monitor(debug=False)
mon.titles   = ['AdytumDNS','AdytumMail','AdytumWeb','AdytumShell','WP','SD','W3C',]
mon.host_list   = [
  'dns2.adytum.us',
  'mail2.adytum.us',
  'www2.adytum.us',
  'shell2.adytum.us',
  'washingtonpost.com',
  'slashdot.org',
  'w3.org',
]  
mon.warn_thresh = [ 67,67,67,67,67,67,67 ]
mon.err_thresh  = [ 25,25,25,25,25,25,25 ]
mon.notification_list = [
  'duncan.mcgreggor@adytumsolutions.com',
]
mon.hostsPingMonitor()

###########################
# Remote: Adytum Server 2 #
###########################
mon = Monitor.Monitor(debug=False)
mon.remote_host = 'shell2.adytum.us'
mon.remote_user = 'root'
mon.getRemoteProcessList()
mon.titles      = [ 'Apache2',  'Zope27',   'Divmod Webmail',   'Qmail',    'LDAP',     ]
mon.match_list  = [ 'httpd2',   'run.py',   'quotient.tap',     'qmail',    'slapd',    ]
mon.warn_thresh = [ 4,           2,          0,                  7,         6,          ]
mon.err_thresh  = [ 1,           1,          1,                  6,         3,          ]
mon.notification_list = [
  'duncan.mcgreggor@adytumsolutions.com',
]
mon.remoteProcessMonitor()

################
# HTTP Servers #
################
mon = Monitor.Monitor(debug=False)
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


#################
# Data for Zope #
#################
# I'd like to be able to read summary data for external applications
# like Zope, but the problem with that is read conflicts with the
# cron of the process_monitor. To minimize conflicts until I can 
# implement a ZODB/ZEO solution, I will have this script generate a
# pickle file that will write out a summary of current state data,
# and then will copy that file with another name, and that's the one
# that external applications can open.
mon = Monitor.Monitor(debug=False)
mon.summary_pymon = '/tmp/pymon.summary.pymon'
mon.summary_extapp = '/tmp/pymon.summary.external'
mon.saveSummaryData()
mon.copySummaryData()
