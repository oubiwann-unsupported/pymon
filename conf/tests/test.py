'''
>>> import ZConfig
>>> schema = ZConfig.loadSchema('example1.xml')
>>> conf, nil = ZConfig.loadConfig(schema, 'example1.conf')
>>> enabled = conf.monitor_status.enabled
>>> enabled.sort()
>>> enabled
['http status', 'ping']
>>> disabled = conf.monitor_status.disabled
>>> disabled.sort()
>>> disabled
['dns dig', 'http text', 'local process']
'''

def _test():
    import doctest, test
    return doctest.testmod(test)

if __name__ == '__main__':
    _test()

