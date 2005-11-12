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
'''

def _test():
    import doctest, test
    return doctest.testmod(test)

if __name__ == '__main__':
    _test()

