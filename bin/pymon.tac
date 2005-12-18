import pwd, grp

from twisted.python import log
from twisted.application import service

from pymon.config import cfg
from pymon.application import State, History
from pymon.registry import globalRegistry
from pymon import engines
from pymon import servers

# perform registry operations
globalRegistry.add('config', cfg)
state       = State()
history     = History()
factories   = {}
globalRegistry.add(cfg.global_names.state, state)
globalRegistry.add(cfg.global_names.history, history)
globalRegistry.add(cfg.global_names.factories, factories)

# create application and application service container
user        = pwd.getpwnam(cfg.user)[2]
group       = grp.getgrnam(cfg.group)[2]
appname     = cfg.instance_name
application = service.Application(appname, uid=user, gid=group)
pymonsvc    = service.IServiceCollection(application)

# add all the services that are going to be monitored. This is where you
# add service engine; choose the right one for your architecture, for 
# instance:
#
#   engines.runProcessOptimizedEngine()
#
# See pymon.engines for details
engines.runTwistedFactoryEngine(pymonsvc)

# Add a local perspective broker server for running processes
servers.addProcessServer(pymonsvc)

# Add a Nevow web server to pymon for the HTTP interface
servers.addWebServer(pymonsvc)

#servers.addXMLRPCServer(pymonsvc)
#servers.addSNMPServer(pymonsvc)

# Schedule regular backups of state data to disk
# XXX examine twisted.application's use of persisted data through restarts;
# maybe use theirs instead.
servers.addBackupServer(pymonsvc)
