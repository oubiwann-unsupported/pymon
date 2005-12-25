import os
import sys
import pwd, grp
from pkg_resources import require
require('Adytum-PyMonitor >= 1.0.4')
from adytum.config import zconfig
import ZConfig 

schema = ZConfig.loadSchema('etc/schema.xml')
cfg, nil = ZConfig.loadConfig(schema, 'etc/pymon.conf')

uid = pwd.getpwnam(cfg.user)[2]
gid = grp.getgrnam(cfg.group)[2]

# Create links in cfg.prefix to the installed binaries
src_bin_dir = os.path.join(sys.exec_prefix, 'bin')
dst_bin_dir = os.path.join(*cfg.prefix.split('/')+['bin'])
# XXX this isn't cooperating with the setuptools stuff and needs to
# be fixed
'''
for bin in ['pymon', 'pymon.tac']:
    src = os.path.join(src_bin_dir, bin)
    dst = os.path.sep+os.path.join(dst_bin_dir, bin)
    print "Linking %s to %s..." % (src, dst)
    try:
        os.symlink(src, dst)
    except OSError:
        print "Already linked; skipping."
'''
for bin in ['pymond', 'pymon.tac']:
    src = open(os.path.join('./bin', bin))
    dst = os.path.sep+os.path.join(dst_bin_dir, bin)
    try:
        os.remove(dst)
    except OSError:
        # doesn't exist; don't worry about it
        pass
    dstfh = open(dst, 'w+')
    dstfh.write(src.read())
    os.system('chmod 755 %s' % dst)

print "Copying web files..."
os.system('cp -r static %s' % cfg.prefix)

print "Copying daemontools files..."
os.system('cp -r service %s' % cfg.prefix)

# Set the permissions on the install directory
print "Changing ownership of %s to %s:%s (%s:%s)..." % (cfg.prefix, 
    cfg.user, cfg.group, uid, gid)

for fullpath, dirs, files in os.walk(cfg.prefix):
    os.chown(fullpath, uid, gid)
    for filename in files:
        os.chown(os.path.join(fullpath, filename), uid, gid)
