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
 
