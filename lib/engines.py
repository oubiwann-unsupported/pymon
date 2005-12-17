from twisted.application import internet

from pymon.registry import globalRegistry
from pymon import utils
from pymon import monitors

# XXX need to add support for service groups here...
# XXX if factories are iterated through first and instantiated,
# the twisted factory's state machine can be used for each 
# state instead of our custom global state machine. There are
# circumstances under this would not be ideal, though, and so
# may require that we offer different "tuning" options.
def runTwistedFactoryEngine(rootService):
    cfg = globalRegistry.config
    types = cfg.enabled.services.service_type
    if not isinstance(types, list): 
        types = [types]
    for type in types:
        for service in cfg.services.service(type=type).entries.entry:
            enabled = service.enabled.capitalize()
            if enabled == 'True':
                uid = utils.makeUri(type, service.uri)
                factory = monitors.AbstractFactory(uid)
                globalRegistry.factories.update({uid:factory})

                monitor = factory.makeMonitor()
                service = internet.TimerService(monitor.getInterval(), monitor)
                service.setServiceParent(rootService)

def runHighCheckVolumeEngine(rootService):
    pass

def runLowCheckVolumeEngine(rootService):
    pass

def runProcessOptimizedEngine(rootService):
    pass

