import os
import sys
import time
import pwd, grp
import filecmp
from urllib2 import urlparse

build_dir = os.path.join('build', 'third-party')
try:
    os.makedirs(build_dir)
except OSError:
    # Path exists
    pass

if sys.version_info[0:3] < (2,4):
    print """pymon requires version python 2.4 or greater."""
    sys.exit()

def pyInstall(url, unpak, unpakt):
    prot, host, path, nil, nil, nil = urlparse.urlparse(url)
    if not os.path.exists(os.path.join(build_dir, unpakt)):
        print "\nDownloading %s..." % url 
        if unpak == 'unzip':
            os.system('cd %s;wget %s;%s %s.zip;rm %s.zip' % (
                build_dir, url, unpak, unpakt, unpakt))
        else:
            os.system('cd %s;wget -qO - %s|%s' % (build_dir, url, 
                unpak))
    print "\nInstalling %s..." % unpakt
    os.system('cd %s;cd %s;%s setup.py install' % (build_dir, unpakt, 
        sys.executable))
    time.sleep(2)

# Process all the dependencies
deps = eval(open('DEPENDENCIES').read())
for name, url, unpak, unpakt, force in deps['python_packages']:
    # Do we need to install it?
    try:
        exec("import %s" % name)
        print "%s is installed." % name
    except ImportError:
        print "%s not installed." % name
        pyInstall(url, unpak, unpakt)
    if force:
        pyInstall(url, unpak, unpakt)

# Make sure that the most recent version of the support modules are 
# loaded
from pkg_resources import require
require('Adytum-PyMonitor >= 1.0.4')

# Now that we have all the stuff we need, we can procede
import ZConfig 

schema = ZConfig.loadSchema('etc/schema.xml')
cfg, nil = ZConfig.loadConfig(schema, 'etc/pymon.conf')

# User/Group check
try:
    uid = pwd.getpwnam(cfg.user)[2]
    gid = grp.getgrnam(cfg.group)[2]
except KeyError:
    print """
Non-system user or group name given.  Did you create the user and
group, and then edit your copied ./etc/pymon.con file?\n"""
    sys.exit()

# Create the necessary directories
paths = ['bin', 'etc', 'var', 'log', 
    os.path.join(
        cfg.admin.backups.base_dir,
        cfg.admin.backups.state_dir),
]
for path in paths:
    dir = os.path.join(cfg.prefix, path)
    try:
        os.makedirs(dir)
        print "Created directory %s." % dir
    except OSError:
        # Path already exists
        pass

### Sensitive Files -- this is for files that users/administrator
# will be customizing, which we do not want setup to overwrite.
SENSITIVE_FILES = [
    'etc/pymon.conf',
    ]

for filename in SENSITIVE_FILES:
    # Get data
    data = open(filename).read()
    # Check if file exists
    outfile = os.path.join(cfg.prefix, filename)
    if os.path.exists(outfile):
        if not filecmp.cmp(filename, outfile, False):
            print "File '%s' already exists and is different." % outfile
            outfile = outfile + ".new"
            print "Creating file '%s'." % outfile
    # Write file
    out = open(outfile, 'w+')
    out.write(data)
    out.close()



