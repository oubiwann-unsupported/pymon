import os
import sys
import pwd, grp
import filecmp
from urllib2 import urlparse

import ZConfig 

schema = ZConfig.loadSchema('etc/schema.xml')
cfg, nil = ZConfig.loadConfig(schema, 'etc/pymon.conf')

build_dir = os.path.join('build', 'third-party')
try:
    os.makedirs(build_dir)
except OSError:
    # path exists
    pass

if sys.version_info[0:3] < (2,4):
    print """pymon requires version python 2.4 or greater."""
    sys.exit()

def pyInstall(url, unpak, unpakt):
    unpakt = os.path.join(build_dir, unpakt)
    prot, host, path, nil, nil, nil = urlparse.urlparse(url)
    if not os.path.exists(unpakt):
        print "\nDownloading %s..." % url 
        os.system('cd %s;wget -q -O - %s|%s' % (build_dir, url, 
            unpak))
    print "\nInstalling %s..." % unpakt
    os.system('cd %s;%s setup.py build' % (unpakt, sys.executable))

deps = eval(open('DEPENDENCIES').read())
for name, url, unpak, unpakt in deps['python_packages']:
    # do we need to install it?
    #try:
    #    exec("import %s" % name)
    #except ImportError:
    print "%s not installed." % name
    pyInstall(url, unpak, unpakt)

try:
    uid = pwd.getpwnam(USER)[2]
    gid = grp.getgrnam(GROUP)[2]
except KeyError:
    print """\nNon-system user or group name given. 
Did you edit the ./lib/app/pymon/constants.py file?\n"""
    sys.exit()

### Sensitive Files -- this is for files that users/administrator
# will be customizing, which we do not want setup to overwrite.
SENSITIVE_FILES = [
    'etc/pymon.conf',
    ]
for filename in SENSITIVE_FILES:
    # get data
    data = open(filename).read()

    # check if file exists
    outfile = os.path.join(cfg.prefix, filename)
    if os.path.exists(outfile):
        if not filecmp.cmp(filename, outfile, False):
            print "File '%s' already exists and is different." % outfile
            outfile = outfile + ".new"
            print "Creating file '%s'." % outfile

    # write file
    out = open(outfile, 'w+')
    out.write(data)
    out.close()

print "Changing ownership of %s to %s:%s (%s:%s)..." % (cfg.prefix, cfg.user, cfg.group, uid, gid)
for fullpath, dirs, files in os.walk(cfg.prefix):
    os.chown(fullpath, uid, gid)
    for filename in files:
        os.chown(os.path.join(fullpath, filename), uid, gid)

