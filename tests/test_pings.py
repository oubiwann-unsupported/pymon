import sys
sys.path.append('../')
from System.Hosts import HostsUp


check = HostsUp(host='shell2.adytum.us', counts=4)
print check.getPingPercent()

