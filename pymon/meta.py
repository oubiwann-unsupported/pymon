display_name = "pymon"
library_name = "pymon"
version = "0.3.8"
author = "Duncan McGreggor"
author_email = "oubiwann@gmail.com"
license = "BSD"
url = "http://launchpad.net/pymon"
description = "An open source distributed networked resources monitoring system."
long_description = """pymon is an open source network and process monitoring
solution implemented in Twisted. It's built for use and deployment in
distributed environments. Both the interface and the software configuration are
designed to be easily and rapidly updated, saving on time and overhead often
associated with other monitoring solutions."""
requirements = [
    "txmongo",
    "nevow",
    "twisted",
    "pyOpenSSL",
    "PyYAML",
    "zope.interface",
    ]
