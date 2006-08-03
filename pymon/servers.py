from twisted.application import internet

from nevow import vhost
from nevow import appserver

import utils
import agents
from ui.web import pages
from application import globalRegistry

log = utils.log

def refreshConfig():
    log.info("Checking for config file changes...")
    conf_file = getResource(['etc', 'pymon.conf'])
    conf = open(conf_file).read()
    new_md5 = md5.new(conf).hexdigest()
    old_md5 = globalRegistry.state.get('config_md5')
    globalRegistry.state['config_md5'] = new_md5
    # check against MD5 in state
    if new_md5 != old_md5:
        log.warning("Config MD5 signatures do not match; loading new config...")
        # get and load schema, load config
        schema_file = getResource(['etc', 'schema.xml'])
        schema = ZConfig.loadSchema(schema_file)
        cfg, nil = ZConfig.loadConfig(schema, conf_file)
        # set global config to newly loaded config
        globalRegistry.config = cfg
        #if cfg.daemontools_enabled:
        #    subprocess.call('svc', '-t %s' % cfg.daemontools_service)

def publishJSON():
    '''
    This is a function for peering but the data is only for the local
    pymon installtion.
    '''
    log.info("Publishing JSON data...")
    # iterate through each monitor's state data, convert to JSON, and then
    # write to a file in the the configured static JSON directory

    # copy the configuration file to a static location
    # enable this only if you don't have sensitive information in your
    # configuration file

def checkPeers(cfg):
    '''
    The function that is called when periodically checking pymon peers.
    '''
    # XXX This function may not ever get used. It may be more economical
    # to simply make XHR's from JavaScript to the pymon peers.
    log.info("Checking peers...")
    for peer in cfg.peers.urls:
        # get file?
        # copy file?
        # or just let JS do it in the web client?
        # to let the client do it, we'll need to use nevow to set a cookie
        log.info("Cheeking peer '%s'..." % peer) 

def addWebServer(rootService):
    factories = globalRegistry.factories
    vResource = vhost.VHostMonsterResource()
    webroot = pages.Root(factories)
    webroot.putChild(rootService.cfg.web.vhost_root, vResource)
    site = appserver.NevowSite(webroot)
    port = int(rootService.cfg.web.port)
    webserver = internet.TCPServer(port, site)
    webserver.setServiceParent(rootService)

def addConfigServer(rootService):
    interval = int(rootService.cfg.admin.config_update.interval)
    #config_check = internet.TimerService(interval, refreshConfig)
    config_check = internet.TimerService(interval, lambda x: None, '')
    config_check.setServiceParent(rootService)

def addBackupServer(rootService):
    interval = int(rootService.cfg.admin.backups.interval)
    backups = internet.TimerService(interval, 
        globalRegistry.state.save)
    backups.setServiceParent(rootService)

def addProcessServer(rootService):
    factory = agents.ProcessServerFactory()
    port = int(rootService.cfg.agents.port)
    server = internet.TCPServer(port, factory)
    server.setServiceParent(rootService)

def addJSONPublisher(rootService):
    interval = int(rootService.cfg.admin.peering.publish_interval)
    publisher = internet.TimerService(interval, publishJSON)
    publisher.setServiceParent(rootService)

def addPeerChecker(rootService):
    interval = int(rootService.cfg.admin.peering.check_interval)
    peerChecker = internet.TimerService(interval, checkPeers,
        rootService.cfg)
    peerChecker.setServiceParent(rootService)
