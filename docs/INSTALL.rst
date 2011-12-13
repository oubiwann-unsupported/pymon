======================
dependancies
======================

System dependencies
-------------------
* Python 2.4 - python2.4 needs to be in your path
* a program named "sendmail" that is in your path and can send mail
* standard C header files

Python Dependencies
-------------------
These are automatically downloaded and installed for you. I
had planned on using EasyInstall for this, but alas, many people
are not producing setup.py files that are EasyInstall-friendly. As
the maintainers of the software upon which we depend make their
stuff EasyInstall-ready, these will shift into the setup.py file,
to be handled by setuptools/EasyInstall.

If you are having troubles with setuptools and/or the package
"pkg_resources", you may have an older version installed. To resolve
these issues, you will very likely have to manually install setuptools
using the -D option to delete the older versions. To begin
troubleshooting it, you may want to start up a python session,
running the following (since the ez_setup script hides errors in
try/except blocks)::

    $ python2.4
    >>> import pkg_resources
    >>> pkg_resources.require("setuptools>=0.6a8")

Removing ``PYTHON_LIB/site-packages/setuptools-OFFENDING_VERS.egg`` has
always worked for me.

Please note, that if you have Twisted installed already, the
auto-installer won't install it. But pymon requires Twisted 2.1.0,
because it uses the Epsilon package, so you will need to manually
install/upgrade your Twisted if you have anything less than 2.1.0.

Configuration
-------------

``*** IMPORTANT ***``

You must create a copy of ``etc/example-pymon.conf`` and name it
"etc/pymon.conf". The install script setup.py will not run
without it.

You don't have to have your whole monitoring scheme planned out and
configured in your pymon.conf -- but you do need to indicate prefix (install
location), user, and group. After installation, you can then edit your
installed pymon.conf file (PREFIX/etc/pymon.conf) for all the services
that you want to monitor.

Installation
------------
NOTE: during the current development phase, we are not testing the complete
installation process, and we are probably breaking it in places. As a result,
if you wish to run pymon, do the following:

  * define ``PYTHONPATH`` to include the current directory
  * check out the latest pymon from git (see the README)
  * ``cd`` to the pymon checkout directory
  * run ``python presetup.py`` to install the dependencies

(The rest of the install instructions will eventually be applicable, but are
currently not supported)

To install the application with all the defaults, simply run the
usual::

  sudo python setup.py install

This will install the required python libraries, "binaries",
configuration files, and a daemontools setup. The python libraries
will be installed in the usual place (site-packages), and all the
pymon files you might need to change and/or configure, will be
installed in PREFIX.

Running pymon
-------------
See the README for instructions on running pymon.
