'''
# thinking about how this would be used...
config.services = []
service.type
service.defaults.ping_count
service.hosts = []
host.name
host.escalation.enabled
host.escalation.groups = []
group.level
group.emails = []

# and then from the attribute perspective:
config.services.service.type
config.services.service.defaults.ping_count
config.services.service.hosts
config.services.service.hosts.host.name
config.services.service.hosts.host.escalation.enabled
config.services.service.hosts.host.escalation.groups
config.services.service.hosts.host.escalation.groups.group.level
config.services.service.hosts.host.escalation.groups.group.emails

Hmmm... so, unlink the dictionary that would spawn this, the 
names here would only be valid in contexts, or rather, the
values would change depending upon the context. 

Said another way, these dotted names are not unique 
identifiers.

'''
maillist1 = ['oubiwann@myrealbox.com', 'oubiwann@yahoo.com']
maillist2 = []
maillist3 = ['oubiwann@yahoo.com']
maillist4 = ['oubiwann@myrealbox.com']
groups = {
    'level0': maillist1,
    'level1': maillist4,
}
escalation = {
    'enabled': True,
    'groups': groups,
}

hosts = [
    {
        'name': 'shell1.adytum.us',
        'escalation': escalation,
    },
    {
        'name': 'shell2.adytum.us',
        'escalation': escalation,
    },
] # this can be a list

defaults = {
    'ping_count': 4,
    'service_name': 'connectivity',
    'message_template': 'There was a %s%% ping return from host %s',
    'ping_binary': '/bin/ping',
    'command': 'ping',
    'ok_threshold': (67,100),
    'warn_threshold': (26,66),
    'error_threshold': (0,25),
}
service = {
    'type': 'ping',
    'defaults': defaults,
    'hosts': hosts,
}
config = {
    'services': [
        {
            'type': 'ping',
            'defaults': defaults,
            'hosts': hosts,
        },{
            'type': 'http',
            'defaults': None,
            'hosts': None,
        },
    ],
    'system': {
        'database': {
            'type': 'zodb',
            'directory': 'data/zodb',
            'host': 'localhost',
            'port': None,
            'user': None,
            'password': None,
        },
    },
}

'''
Examples:
>>> cfg.system.database.type
'zodb'
>>> cfg.system.database.directory
'data/zodb'
>>> cfg.system.database.host     
'localhost'
>>> cfg.system.database.user
>>> for i in cfg.services:
...   i.type 
... 
'ping'
'http'
'''

'''
Rules:
For each service: name it, get the defaults, build a list of hosts
For each host: enable or disable escalation, build escalation levels
For each escalation level: name it, add a maillist
'''

''' pprint.pprint(config) '''
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

