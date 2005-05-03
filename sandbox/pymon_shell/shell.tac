import sys
sys.path.append('.')
from deployment import deploy

#d = {}
#execfile("config", {}, d)

#print d
application = deploy(
    hostname='dev.adytum.us', 
    instancename='pymon01')
