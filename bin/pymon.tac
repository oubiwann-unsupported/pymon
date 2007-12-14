from twisted.application import service

from pymon.config import cfg
from pymon import engines
from pymon import services

# create application and application service container
#user, group = cfg.getPymonUserGroup()
appname = cfg.instance_name
#application = service.Application(appname, uid=user, gid=group)
application = service.Application(appname)
pymonsvc = service.IServiceCollection(application)
pymonsvc.cfg = cfg

# add all the services that are going to be monitored. This is where you
# add service engine; choose the right one for your architecture, for
# instance:
#
#   engines.runProcessOptimizedEngine()
#
# See pymon.engines for details
engines.runTwistedFactoryEngine(pymonsvc)

# Add a local perspective broker server for running processes
services.addProcessServer(pymonsvc)

# Add a Nevow web server to pymon for the HTTP interface
services.addWebServer(pymonsvc)

#servers.addXMLRPCServer(pymonsvc)
#servers.addSNMPServer(pymonsvc)

# Schedule regular tasks
# XXX examine twisted.application's use of persisted data through restarts;
# maybe use their backups instead.
services.addConfigServer(pymonsvc)
services.addBackupServer(pymonsvc)

# Support for distributed pymon
services.addJSONPublisher(pymonsvc)
services.addPeerChecker(pymonsvc)
