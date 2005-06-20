from interfaces.config import *

'''
Here's a sample dict upon which I am basing this config:

{'services': [{'defaults': {'command': 'ping',
                            'error_threshold': (0, 25),
                            'message_template': 'There was a %s%% ping return from host %s',
                            'ok_threshold': (67, 100),
                            'ping_binary': '/bin/ping',
                            'ping_count': 4,
                            'service_name': 'connectivity',
                            'warn_threshold': (26, 66)},
               'hosts': [{'escalation': {'enabled': True,
                                         'groups': {'level0': ['oubiwann@myrealbox.com',
                                                               'oubiwann@yahoo.com'],
                                                    'level1': ['oubiwann@myrealbox.com']}},
                          'name': 'shell1.adytum.us'},
                         {'escalation': {'enabled': True,
                                         'groups': {'level0': ['oubiwann@myrealbox.com',
                                                               'oubiwann@yahoo.com'],
                                                    'level1': ['oubiwann@myrealbox.com']}},
                          'name': 'shell2.adytum.us'}],
               'type': 'ping'},
              {'hosts': None, 'type': 'http', 'defaults': None}],
 'system': {'database': {'directory': 'data/zodb',
                         'host': 'localhost',
                         'password': None,
                         'port': None,
                         'type': 'zodb',
                         'user': None}}}
'''
class DictConfig(object):
    def __init__(self, config):
        for key, val in config.items():
            if type(val).__name__ == 'dict':
                subobj = Config(val)
                setattr(self, key, subobj)
            elif type(val).__name__ == 'list':
                l = []
                for element in val:
                    if type(element).__name__ == 'dict':
                        l.append(Config(element))
                    else:
                        l.append(element)
                setattr(self, key, l)
            else:
                setattr(self, key, val)


class DictConfigOld(object):

    def __init__(self, aDict):
        self.config = aDict

    def getServices(self):
        return self.config['services']

    def getServicesOfType(self, service_type):
        return [ x for x in self.getServices() if x['type'] == service_type ]

    def getSystem(self):
        return self.config['services']

    def getConstants(self):
        return self.config['constants']


