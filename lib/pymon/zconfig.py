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
