'''
Dotted notation below is <database>.<collection>.

pymon.service

    Record for monitored service; this is host information and should change
    infrequently (if at all) for steady-state networks. This information is
    used by pymon more as a lookup table than anything else.

    {
        org: u"",
        host: u"",
        service: u"",
        service_type: u"",
        factory: u"",
        config: u""
    }


XXX convert the rest of these to JSON

class Status(object):
    """
    Record for 'current status'
    """
    # XXX add relation for service
    id = Int(primary=True)
    host = Unicode()
    service = Unicode()
    current = Int()
    current_name = Unicode()
    previous = Int()
    previous_name = Unicode()
    message = Unicode()
    data = Unicode()


class Counts(object):
    """
    Record for total number of checks in each of the pymon states.
    """
    # XXX add relation for service
    ok = Int()
    warn = Int()
    error = Int()
    failed = Int()
    unknown = Int()
    maintenance = Int()
    disabled = Int()


class LastTimes(object):
    """
    Record for tracking the last time a service was in any given state.
    """
    check = DateTime()
    ok = DateTime()
    warn = DateTime()
    error = DateTime()
    failed = DateTime()


class Event(object):
    """
    Record for a service's status transitions
    """
    # XXX add relation for service
    id = Int(primary=True)
    host = Unicode()
    service = Unicode()
    current = Int()
    current_name = Unicode()
    previous = Int()
    previous_name = Unicode()
    message = Unicode()
    data = Unicode()
'''
