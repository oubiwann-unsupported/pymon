'''
# load example 1
>>> import ZConfig
>>> schema = ZConfig.loadSchema('example1.xml')
>>> ex1, nil = ZConfig.loadConfig(schema, 'example1.conf')

# test values
>>> ex1.check_by
'services'
>>> enabled = ex1.monitor_status.enabled
>>> enabled.sort()
>>> enabled
['http status', 'ping']
>>> disabled = ex1.monitor_status.disabled
>>> disabled.sort()
>>> disabled
['dns dig', 'http text', 'local process']

# load example 2
>>> schema = ZConfig.loadSchema('example2.xml')
>>> ex2, nil = ZConfig.loadConfig(schema, 'example2.conf')

# test values
>>> ex2.uid
'pymon'
>>> ex2.prefix
'/usr/local/pymon'
>>> ex2.mail_from
'pymon@ixappliance.com'
>>> ex2.backups.interval
300
>>> ex2.state_definitions.ok
1
>>> ex2.state_definitions.warn
3
>>> ex2.state_definitions.error
4

# load example 3
>>> schema = ZConfig.loadSchema('example3.xml')
>>> ex3, nil = ZConfig.loadConfig(schema, 'example3.conf')

# test values
>>> ex3.services.ping_defaults.count
4
>>> ex3.services.ping_defaults.interval
25
>>> ex3.services.ping_defaults.binary
'/sbin/ping'
>>> enabled = [ x.uri for x in ex3.services.pings if x.check_enabled ]
>>> enabled.sort()
>>> enabled
['shell1.adytum.us', 'svn.adytum.us']
>>> ex3.services.ping_defaults.message_template % (100, 'localhost.localdomain')
'There was a 100% ping return from host localhost.localdomain'
>>> ex3.services.ping_defaults.error_message % ('localhost.localdomain', 2)
'pymon ERROR: localhost.localdomain : 2% loss'
>>> emails = ex3.notification_list.emails
>>> emails.sort()
>>> emails
['jojo.idiot@circus_boy.com', 'pretty@new_pet.com']
>>> emails = ex3.services.ping_defaults.notification_list_append.emails
>>> emails.sort()
>>> emails
['living_in_a_van@down-by.the-river.com']
>>> for ping in ex3.services.pings:
...   try:
...     emails = ping.notification_list_replace.emails
...     emails.sort()
...     emails
...   except AttributeError:
...     print "No replace list..."
No replace list...
No replace list...
['bull@butchers-ass.com', 'thick@candy-shell.com']

'''

def _test():
    import doctest, test
    return doctest.testmod(test)

if __name__ == '__main__':
    _test()

