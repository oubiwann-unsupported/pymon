from adytum.util.uri import Uri

class ClientMixin(object):

    def getOkThreshold(self):
        # XXX put this in connectionMade so that we can
        # do self.entity = ent and refer to it in the 
        # rest of the client
        if self.factory.service_cfg.ok_threshold:
            return self.factory.service_cfg.ok_threshold
        else:
            return self.factory.type_defaults.ok_threshold

    def getWarnThreshold(self):
        if self.factory.service_cfg.warn_threshold:
            return self.factory.service_cfg.warn_threshold
        else:
            return self.factory.type_defaults.warn_threshold

    def getErrorThreshold(self):
        if self.factory.service_cfg.error_threshold:
            return self.factory.service_cfg.error_threshold
        else:
            return self.factory.type_defaults.error_threshold
    
    def getMsg(self):
        return self.factory.type_defaults.message_template

    def getHost(self):
        uri = Uri(self.factory.uid)
        return uri.getAuthority().getHost()    
