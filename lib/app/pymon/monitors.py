from adytum.app.pymon import protocols
from adytum.app.pymon.config import pymon as cfg

constants = {'states': cfg.getStateDefs()}

def getPingMonitors():

    pings = []
    defaults = cfg.sections['defaults :: ping']

    for section in cfg.pings:
        # ping config options setup
        pingdata = cfg.sections[section]
        pingcfg = {'defaults':defaults, 'constants':constants, 'data':pingdata}

        # get the info in order to make the next ping
        host = cfg.inidata.get(section, 'destination host')
        count = cfg.inidata.get('defaults :: ping', 'ping count')
        command = defaults['command']
        params = '-c %s' % count
        binary = defaults['ping binary']

        # setup the protocol we need that has all the callbacks
        process = protocols.PyMonPing(pingcfg)
        options = [command, params, host]
        #options = ['ping', '-c %s' % count, '%s' % host]
        data = (process, binary, options)
    
        # add to the pings that will be spawned in the reactor
        pings.append(data)

    return pings

def getHTTPMonitors():

    http = []
    defaults = cfg.sections['defaults :: http']

    for section in cfg.http:
        # http config options setup
        httpdata = cfg.sections[section]
        httpcfg = {'defaults': defaults, 'constants': constants, 'data': httpdata}

        # get the info to make the next http check
        client = protocols.PyMonHTTPClientFactory(httpcfg)
        host = cfg.inidata.get(section, 'destination host')
        if httpdata.has_key('port'):
            port = httpdata['port']
        else:
            port = defaults['port']

        # setup the protocol that has all the callbacks
        data = (host, int(port), client)

        # add to the processes that will be spawned in the reactor
        http.append(data)

    return http

def getLocalProcessMonitors():

    procs = []
    defaults = cfg.sections['defaults :: process']
    
    for section in cfg.local_processes:
        # local process config options setup

        # get the info to make the next process check

        # setup the protocol that has all the callbacks

        # add to the processes that will be spawned in the reactor
        procs.append(data)

    return procs

