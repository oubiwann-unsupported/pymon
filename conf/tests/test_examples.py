'''
# load config
>>> import ZConfig
>>> schema = ZConfig.loadSchema('example4.xml')
>>> conf, nil = ZConfig.loadConfig(schema, 'example4.conf')

# test global enable
>>> conf.check_by
'services'
>>> enabled = conf.monitor_status.enabled
>>> enabled.sort()
>>> enabled
['http status', 'ping']
>>> disabled = conf.monitor_status.disabled
>>> disabled.sort()
>>> disabled
['dns dig', 'http text', 'local process']

# test top-level keys
>>> conf.uid
'pymon'
>>> conf.prefix
'/usr/local/pymon'
>>> conf.mail_from
'pymon@ixappliance.com'
>>> conf.backups.interval
300
>>> conf.state_definitions.ok
1
>>> conf.state_definitions.warn
3
>>> conf.state_definitions.error
4

# test ping checks
>>> conf.services.ping.defaults.count
4
>>> conf.services.ping.defaults.interval
25
>>> conf.services.ping.defaults.binary
'/sbin/ping'
>>> enabled = [ x.uri for x in conf.services.ping.checks if x.enabled ]
>>> enabled.sort()
>>> enabled
['shell1.adytum.us', 'svn.adytum.us']
>>> conf.services.ping.defaults.message_template % (100, 'localhost.localdomain')
'There was a 100% ping return from host localhost.localdomain'
>>> conf.services.ping.defaults.error_message % ('localhost.localdomain', 2)
'pymon ERROR: localhost.localdomain : 2% loss'

# test notification lists
>>> emails = conf.notification_list.emails
>>> emails.sort()
>>> emails
['jojo.idiot@circus_boy.com', 'pretty@new_pet.com']
>>> emails = conf.services.ping.defaults.notification_list_append.emails
>>> emails.sort()
>>> emails
['living_in_a_van@down-by.the-river.com']
>>> for ping in conf.services.ping.checks:
...   try:
...     emails = ping.notification_list_replace.emails
...     emails.sort()
...     emails
...   except AttributeError:
...     print "No replace list..."
No replace list...
No replace list...
['bull@butchers-ass.com', 'thick@candy-shell.com']

# test scheduled downtime dates
>>> for ping in conf.services.ping.checks:
...   try:
...     ping.scheduled_downtime['start'].timetuple()
...     ping.scheduled_downtime['end'].timetuple()
...   except:
...     print "No scheduled outages..."
No scheduled outages...
(2005, 12, 1, 3, 0, 0, 3, 335, -1)
(2005, 12, 1, 4, 0, 0, 3, 335, -1)
No scheduled outages...

# test http thresholds
>>> conf.services.http_status.defaults.ok_threshold
[100, 101, 200, 201, 202, 203, 300, 302, 303, 304, 305]
>>> conf.services.http_status.checks[1].ok_threshold
[200]
>>> conf.services.http_status.checks[1].warn_threshold
[100, 101, 201, 202, 203, 204, 205, 206, 300, 301, 302, 303, 304, 305, 401, 402, 403, 405, 406, 407, 411, 412, 413, 414, 415, 416]
>>> conf.services.http_status.checks[1].error_threshold
[400, 404, 408, 409, 410, 417, 500, 501, 502, 503, 504, 505]
'''

def _test():
    import doctest, test
    return doctest.testmod(test)

if __name__ == '__main__':
    _test()

