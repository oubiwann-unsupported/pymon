import os
from pkg_resources import Requirement, resource_filename

from twisted.python import log

import ZConfig

egg_pkg_name = "PyMonitor"
schema_file = resource_filename(Requirement.parse(egg_pkg_name),
    "etc/schema.xml")
config_file = resource_filename(Requirement.parse(egg_pkg_name),
    "etc/pymon.conf")
schema = ZConfig.loadSchema(schema_file)
cfg, nil = ZConfig.loadConfig(schema, config_file)

# now that we've got the config file, we can get the prefix and then
# check to see if there is an override on the filesystem for SonicVault
# configuration. If so, we will override the one in the python lib.
prefix = cfg.prefix.split('/')
config_file = os.path.sep + os.path.join(*prefix+['etc', 
    'pymon.conf'])
if os.path.exists(config_file):
    cfg, nil = ZConfig.loadConfig(schema, config_file)

def getResource(rsrc_list):
    prefix = cfg.prefix.split('/')
    rel_path = '/'.join(rsrc_list)
    abs_path = os.path.sep + os.path.join(*prefix+rsrc_list)
    if os.path.exists(abs_path):
        return abs_path
    else:
        return resource_filename(Requirement.parse(egg_pkg_name), 
            rel_path)

# need to call these so pkg_resources caches the files that
# ZConfig will look for by relative path from the cache
resource_filename(Requirement.parse("PyMonitor"),"conf")

# now get teh config
schema_filename = resource_filename(
    Requirement.parse("PyMonitor"),"conf/schema.xml")
config_filename = resource_filename(
    Requirement.parse("PyMonitor"),"conf/pymon.conf")
working_dir =  resource_filename(
    Requirement.parse("PyMonitor"),"conf")

#os.chdir(working_dir)
schema = ZConfig.loadSchema(schema_filename)
cfg, nil = ZConfig.loadConfig(schema, config_filename)
