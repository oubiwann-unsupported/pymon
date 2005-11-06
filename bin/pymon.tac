import pwd, grp

from twisted.application import service

from adytum.app.pymon.application import State, History
from adytum.app.pymon.registry import globalRegistry
import pdb;pdb.set_trace()
from adytum.app.pymon.config import pymoncfg
from adytum.app.pymon import engines
from adytum.app.pymon import servers

# config has to be done first, as everything else depends upon it.
globalRegistry.add('config', pymoncfg)
state       = State()
history     = History()
factories   = {}
globalRegistry.add(pymoncfg.global_names.state, state)
globalRegistry.add(pymoncfg.global_names.history, history)
globalRegistry.add(pymoncfg.global_names.factories, factories)

# create application and application service container
user        = pwd.getpwnam(pymoncfg.system.uid)[2]
group       = grp.getgrnam(pymoncfg.system.gid)[2]
appname     = pymoncfg.system.instance_name
application = service.Application(appname, uid=user, gid=group)
pymonsvc    = service.IServiceCollection(application)

# add all the services that are going to be monitored. This is where you
# add service engine; choose the right one for your architecture, for 
# instance:
#
#   engines.runProcessOptimizedEngine()
#
# See adytum.app.pymon.engines for details
engines.runTwistedFactoryEngine(pymonsvc)

# Add a local perspective broker server for running processes
servers.addProcessServer(pymonsvc)

# Add a Nevow web server to pymon for the HTTP interface
servers.addWebServer(pymonsvc)

# Schedule regular backups of state data to disk
# XXX examine twisted.application's use of persisted data through restarts;
# maybe use theirs instead.
servers.addBackupServer(pymonsvc)
