'''
Functions for use in the configuration of pymon using the ZConfig
package.
'''
from datetime import datetime
from sets import Set

class ValidateCaseInsensitiveList(object):
    '''
    A class for defining legal list values.
    '''
    def __init__(self, legal_values):
        self.legal_values = legal_values
        format = "'"
        format += "', '".join(self.legal_values[:-1])
        self.formatted_list = "'%s or '%s'" % (format, self.legal_values[-1])

    def validate(self, value):
        if value.lower() in self.legal_values:
            return value
        raise ValueError, (
            "Value must be one of: %s" % self.formatted_list)

def checkBy(value):
    '''
    Validator for the allowed values representing the manner
    in which the monitoring checks are made.
    '''
    legal_values = ['services', 'groups']
    validator = ValidateCaseInsensitiveList(legal_values)
    return validator.validate(value)

def _int(value):
    try:
        return int(value)

    except ValueError:
        raise ValueError, "Value must be coercable to an integer."

def rangedValues(range_string):
    '''
    Validator human-readable, easily/commonly understood format
    representing ranges of values. At it's most basic, the following
    is a good example:
        25-30
    A more complicated range value would be something like:
        20-25, 27, 29, 31-33
    '''
    # XXX need to write a regular expression that really checks for this
    values = []
    ranges = range_string.split(',')
    for value in ranges:
        if '-' in  value:
            start, end = value.split('-')
            start = _int(start.strip())
            end = _int(end.strip())
            values.extend(range(start, end+1))
        else:
            value = _int(value)
            values.append(value)

    # get rid of duplicates
    values = list(Set(values))
    values.sort()

    return values

def logLevel(log_level):
    log_level = log_level.upper()
    legal_values = ['FATAL', 'CRITICAL', 'ERROR',
        'WARNING', 'INFO', 'DEBUG']
    lvls = ', '.join(legal_values)
    if log_level in legal_values:
        return log_level
    else:
        raise ValueError, ('Values for log level' + \
            'must be one of the following: %s' % lvls)

def _parseDate(yyyymmdd_hhmmss_string):
    date, time = yyyymmdd_hhmmss_string.split()
    y, m, d = date.strip().split('.')
    h, min, s = time.strip().split(':')
    date_tuple = [ int(x) for x in (y,m,d,h,min,s) ]

    return datetime(*date_tuple)

def getDateRange(range_string):
    '''
    This string is converted to two datetime.datetime objects in a dict:
        {'start': datetime,
         'end': datetime}
    The range_string itself must be of the form:
        YYYY.MM.DD HH:MM:SS - YYYY.MM.DD HH:MM:SS
    The range_string is split by "-" and stripped of trailing/leading
    spaces.
    '''
    date_start, date_end = range_string.split('-')
    date_start = _parseDate(date_start.strip())
    date_end = _parseDate(date_end.strip())

    return {
        'start': date_start,
        'end': date_end,
    }

