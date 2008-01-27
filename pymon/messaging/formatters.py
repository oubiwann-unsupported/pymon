"""
The 'email' template substitutes a dict requiring the following keys:
    from, to, subject, body
"""
email = ("To: %(to)s\r\n" +
         "MIME-Version: 1.0\r\n" +
         "Content-Type: text/plain; charset=us-ascii\r\n" +
         "From: %(from)s\r\n" +
         "Subject: %(subject)s\r\n" +
         "\r\n" +
         "%(body)s\r\n")
