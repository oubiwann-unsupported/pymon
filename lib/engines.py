from twisted.application import internet

from pymon.registry import globalRegistry
from pymon import utils
from pymon.utils import log
from pymon import monitors

# XXX need to add support for service groups here...
# XXX if factories are iterated through first and instantiated,
# the twisted factory's state machine can be used for each 
# state instead of our custom global state machine. There are
# circumstances under this would not be ideal, though, and so
# may require that we offer different "tuning" options.
def runTwistedFactoryEngine(rootService):
    cfg = globalRegistry.config
    enabled = [ x.replace(' ', '_') for x in 
        cfg.monitor_status.enabled ]
    for pm_service_name in cfg.services.getSectionAttributes():
        if pm_service_name in enabled:
            pm_service = getattr(cfg.services, pm_service_name)
            for check in pm_service.checks:
                uid = utils.makeUri(pm_service_name, check.uri)
                log.debug("Setting up monitor factory for monitor " + \
                    "service %s" % uid)
                factory = monitors.AbstractFactory(uid)
                monitor = factory.makeMonitor()
                # XXX this next line could be a potential memory hog
                globalRegistry.factories.update({uid:monitor})
                service = internet.TimerService(monitor.getInterval(), 
                    monitor)
                service.setServiceParent(rootService)

def runHighCheckVolumeEngine(rootService):
    pass

def runLowCheckVolumeEngine(rootService):
    pass

def runProcessOptimizedEngine(rootService):
    pass

