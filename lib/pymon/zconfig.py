'''
Functions for use in the configuration of pymon using the ZConfig
package.
'''
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
    return range_string
    
