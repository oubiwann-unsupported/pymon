import protocols
from config import pymon as cfg

test_section = 'shell1.adytum.us :: ping'
defaults = cfg.sections['defaults :: ping']
constants = {'states': cfg.getStateDefs()}
pingdata = cfg.sections[test_section]
pingcfg = {'defaults':defaults, 'constants':constants, 'data':pingdata}
process = protocols.PyMonPing(pingcfg)

# test an insert
import datamodel

data = {'serviceType': 'ping', 'serviceMessage': 'There was a 100% ping return from host shell1.adytum.us', 'serviceName': 'connectivity', 'serviceHost': 'shell1.adytum.us', 'uniqueID': 'shell1.adytum.us :: ping', 'serviceStatus': '1'}
insert = datamodel.Service(**data)

# test a select
select = datamodel.Service.select(datamodel.Service.uniqueID=='shell1.adytum.us :: ping')
results = select[0:1]

