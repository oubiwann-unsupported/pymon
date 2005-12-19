import os
import sys
import pwd, grp
import ZConfig 

schema = ZConfig.loadSchema('etc/schema.xml')
cfg, nil = ZConfig.loadConfig(schema, 'etc/pymon.conf')

uid = pwd.getpwnam(cfg.user)[2]
gid = grp.getgrnam(cfg.group)[2]

# Set the permissions on the install directory
print "Changing ownership of %s to %s:%s (%s:%s)..." % (cfg.prefix, 
    cfg.user, cfg.group, uid, gid)

for fullpath, dirs, files in os.walk(cfg.prefix):
    os.chown(fullpath, uid, gid)
    for filename in files:
        os.chown(os.path.join(fullpath, filename), uid, gid)

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
for bin in ['pymon', 'pymon.tac']:
    src = open(os.path.join('./bin', bin))
    dst = os.path.sep+os.path.join(dst_bin_dir, bin)
    os.remove(dst)
    dst = open(dst, 'w')
    dst.write(src.read())
    
