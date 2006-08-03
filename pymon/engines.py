from twisted.application import internet

import config
import monitors
from utils import log
from application import globalRegistry

# XXX need to add support for service groups here...
# XXX if factories are iterated through first and instantiated,
# the twisted factory's state machine can be used for each 
# state instead of our custom global state machine. There are
# circumstances under this would not be ideal, though, and so
# may require that we offer different "tuning" options.
def runTwistedFactoryEngine(rootService):
    enabledServices = config.getEnabledServices()
    log.debug("Enabled services: "+str(enabledServices))
    # iterate through the enabled services
    for serviceName in enabledServices:
        log.debug("Service name: "+serviceName)
        pymonService = config.getServicesOfType(serviceName)
        # for each enabled service, iterate through the checks for that 
        # service
        for check in pymonService.checks:
            log.debug("Service check uri: "+check.uri)
            factory = monitors.AbstractFactory(serviceName, check.uri)
            monitor = factory.makeMonitor(rootService.cfg)
            # we might want to do something more like this:
            #   * make sure every monitor implements its own interface
            #   * make sure that interface extends IMonitor
            #   * monitor.uid = uid
            #   * gR.factories.append(monitor)
            # then, to get the monitors we want in the future, we 
            # just do this:
            #   * desired = [ x for x in gR.factories if 
            #       IDesiredMonitor in providedBy(x) ]
            # XXX this next line could be a potential memory hog
            globalRegistry.factories.update({monitor.uid:monitor})
            interval = monitor.getInterval()
            log.debug("Service interval: "+str(interval))
            service = internet.TimerService(interval, monitor)
            service.setServiceParent(rootService)

def runHighCheckVolumeEngine(rootService):
    pass

def runLowCheckVolumeEngine(rootService):
    pass

def runProcessOptimizedEngine(rootService):
    pass

