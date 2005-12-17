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

class LocalMail(Email):

    def setSendmailBinary(self, bin='/usr/sbin/sendmail'):
        self.sendmail = bin

    def send(self):
        import os
        self._prepMessage()
        p = os.popen("%s -t" % self.sendmail, "w")
        p.write(self.mail_data)
        sts = p.close()
        #return sts
        #if sts != 0:
        #    print "Sendmail exit status", sts

class RemoteMail(Email):

    def setHost(self, host):
        self.host = host

    def send(self):
        import smtplib
        self._prepMessage()
        mail=smtplib.SMTP(self.host)
        mail.sendmail(self.frm,self.to,self.mail_data)
        mail.close()
 
