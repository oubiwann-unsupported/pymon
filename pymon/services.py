from twisted.application import internet

from nevow import vhost
from nevow import appserver

from pymon import utils
from pymon.agents import local
from pymon.messaging import listener
from pymon.utils.logger import log
from pymon.config import refreshConfig
from pymon.ui.web import pages
from pymon.application import globalRegistry


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
    for peer in cfg.peers.url:
        log.info("Cheeking peer '%s'..." % peer)
        # get file?
        # copy file?
        # or just let JS do it in the web client?
        # to let the client do it, we'll need to use nevow to set a cookie


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
    #configCheck = internet.TimerService(interval, refreshConfig)
    configCheck = internet.TimerService(interval, lambda x: None, '')
    configCheck.setServiceParent(rootService)


def addBackupServer(rootService):
    interval = int(rootService.cfg.admin.backups.interval)
    backups = internet.TimerService(interval,
        globalRegistry.state.save)
    backups.setServiceParent(rootService)


def addProcessServer(rootService):
    factory = local.ProcessServerFactory()
    port = int(rootService.cfg.agents.local_command.port)
    server = internet.TCPServer(port, factory)
    server.setServiceParent(rootService)


def addMessagingServer(rootService):
    factory = listener.ListenerFactory()
    port = int(rootService.cfg.agents.messaging.port)
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
