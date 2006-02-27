import sys
import logging as log

from pymon.config import cfg

log_level = eval('log.%s' % cfg.log_level)
log.basicConfig(level=log_level,
    format='%(levelname)-8s %(message)s',
    stream=sys.stdout,
)
