import smtplib
from time import ctime

class Mail:

  def mail(self, mail_to='', mail_from='', subject='', body='', host=''):

    body = "MIME-Version: 1.0\r\nContent-Type: text/plain; charset=us-ascii\r\n\r\n" + body

    try:
      message='From: %s\r\nTo: %s\r\nSubject: %s\r\n%s'%(mail_from,mail_to,subject,body)            
      mail=smtplib.SMTP(host)
      mail.sendmail(mail_from,mail_to,message)
      mail.close()
    except:
      try:
        # Logon to the host... If needed
        message='From: %s\r\nTo: %s\r\nSubject: %s\r\n%s'%(mail_from,mail_to,subject,body)
        mail=smtplib.SMTP(host)
        mail.login(User,Pass) 
        mail.sendmail(mail_from,mail_to,message)
        mail.close()
      except:
        pass
        #print 'ERROR: Unable to send notification! - ' + ctime()
