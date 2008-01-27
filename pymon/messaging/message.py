class Message(object):
    def __init__(self, type='', content='', host='localhost', service='ping'):
        self.type = type
        self.content = content
        self.host = host
        self.service = service
