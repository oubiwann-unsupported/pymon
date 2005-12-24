import pwd, grp

from twisted.application import service

from pymon.config import cfg
from pymon import engines
from pymon import servers

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

# Schedule regular tasks
# XXX examine twisted.application's use of persisted data through restarts;
# maybe use their backups instead.
servers.addConfigServer(pymonsvc)
servers.addBackupServer(pymonsvc)
