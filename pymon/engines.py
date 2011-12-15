from twisted.application import internet

from pymon import monitors
from pymon.utils.logger import log
from pymon.application import globalRegistry


# XXX need to add support for service groups here...
# XXX if factories are iterated through first and instantiated,
# the twisted factory's state machine can be used for each
# state instead of our custom global state machine. There are
# circumstances under this would not be ideal, though, and so
# may require that we offer different "tuning" options.
def runTwistedFactoryEngine(rootService):
    cfg = rootService.cfg
    enabledServices = cfg.getEnabledServices()
    # iterate through the enabled services
    for pymonService in enabledServices:
        serviceName = pymonService.getName()
        log.debug("Service name: " + serviceName)
        factoryName = pymonService.default.factory
        # for each enabled service, iterate through the checks for that
        # service
        for check in pymonService.checks:
            log.debug("Service check uri: "+check.uri)
            factory = monitors.AbstractFactory(factoryName, serviceName,
                                               check.uri)
            monitor = factory.makeMonitor(cfg.configFactory(factory.uid))
            # XXX this next line could be a potential memory hog
            globalRegistry.factories.update({monitor.uid:monitor})
            interval = monitor.getInterval()
            log.debug("Service interval: %s" % interval)
            service = internet.TimerService(interval, monitor)
            service.setServiceParent(rootService)


def runHighCheckVolumeEngine(rootService):
    pass


def runLowCheckVolumeEngine(rootService):
    pass


def runProcessOptimizedEngine(rootService):
    pass

