from adytum.app.pymon.datamodel import Service
from adytum.app.pymon.config import pymon as cfg

states = cfg.getStateDefs()
lookup = dict(zip(states.values(), states.keys()))

def updateDatabase(data):

    uid = data['uniqueID']
    select = Service.select(Service.q.uniqueID==uid)
    #print select
    #print select.count()
    if not select.count():
        insert = Service(**data)
        print "Inserting data..."
    else:
        r = select[0]
        prev = r.serviceStatus
        curr = data['serviceStatus']
        if curr == states['ok'] and prev != states['ok'] and prev != states['recovering']:
            curr = states['recovering']
        lastO = r.lastOK
        lastW = r.lastWarn
        lastE = r.lastError
        update = {
            'serviceStatus': curr,
            'serviceMessage': data['serviceMessage'],
            'previousState': prev,
            'lastOK': lastO,
            'lastWarn': lastW,
            'lastError': lastE,
        }
        print "Updating data..."
        r.set(**update)
        print "Getting results for %s:" % uid
        print "Previous state: %s" % lookup[str(r.previousState)].upper()
        print "Current state: %s" % lookup[str(r.serviceStatus)].upper()
