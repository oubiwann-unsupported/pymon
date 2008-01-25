class Email(object):
    def __init__(self, frm='', to='', subj='', data='', host=''):
        self.frm = frm
        self.to = to
        self.subj = subj
        self.msg = data

    def setFrom(self, frm):
        self.frm = frm

    def setTo(self, to):
        self.to = to

    def setSubject(self, subj):
        self.subj = subj

    def setData(self, data):
        self.msg = data

    def _prepMessage(self):
        self.msg = "MIME-Version: 1.0\r\nContent-Type: text/plain; charset=us-ascii\r\n\r\n" + self.msg
        self.mail_data = 'From: %s\r\nTo: %s\r\nSubject: %s\r\n%s'%(self.frm,self.to,self.subj,self.msg)

    def send(self):
        pass
