============
installation
============
Please see the docs/INSTALL file.

=============
running pymon
=============
If the python scripts bin dir is in your path, you can just run the
following::

  sudo pymond

If not, you can add that to your path, but you may as well add
/usr/local/pymon/bin to your path too ;-) Then you can run that
command. If you prefer to not make PATH changes, just run it like this::

  sudo PYMON_PREFIX/bin/pymond

(The default would be "sudo /usr/local/pymon/bin/pymond").

If you would like to run this under daemontools, and you have
daemontools installed, all you have to do is the following:

* edit service/run and make sure that it points to your
  twistd and pymon.tac, and
* ln -s PREFIX/service /service/pymond

If you are running a development version of pymon in your working directory
(svn co), then run the following::
        sudo ./bin/pymond

Now you should be up and running.

apache virtual hosts
--------------------
You can also run pymon under apache configured as a virtual host. Here's
how you'd do that::

  <VirtualHost *:80>
      ServerAdmin netadmin@mycompany.com
      ServerName pymon.mycompany.com
      ProxyPass / http://localhost:8080/vhost/http/pymon.mycompany.com/
  </VirtualHost>

ngix virtual hosts
------------------

TBD

lighttpd virtual hosts
----------------------

TBD

plugin list
-----------
The currently defined monitor types are as follows:

* ping
* http status

port numbers
------------
How the port numbers were chosen::

    >>> from adytum.util import numerology
    >>> numerology.getNumerologicalValue('adytum pymon service web')
    3293
    >>> numerology.getNumerologicalValue('adytum pymon service xml-rpc')
    3298

===========
development
===========

creating a new monitor
----------------------

If you want to add more monitoring types, you will need to:

* add the type to etc/pymon.conf
* add the configuration to etc/schema.xml
* add a new PyMonXXX protocol subclass to lib/protocols.py to
  handle data processing and saving.
* add a XXXMonitor class lib/monitors.py, inheriting from
  MonitorMixin and an appropriate FactoryClass
* update AbstractFactory in lib/monitors.py with a dispatch
  method for instantiating your new monitor class
* enable the new monitoring type in etc/pymon.conf
* rebuild pymon with 'python setup.py install'

For more details, see the development guide: docs/HACKING.txt

contributing
------------

Plans for development are being migrated from the docs/TODO file to a more
formal location using a system specifically designed for targeting feature
development in open source software:

  https://blueprints.launchpad.net/pymon

If the feature you would like to see implemented is not there, feel free to
propose one for discussion.
