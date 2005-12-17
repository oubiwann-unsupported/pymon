# Set the permissions on the install directory
print "Changing ownership of %s to %s:%s (%s:%s)..." % (INSTALL_DIR, USER, GROUP, uid, gid)
for fullpath, dirs, files in os.walk(INSTALL_DIR):
    #print fullpath, dirs, files
    os.chown(fullpath, uid, gid)
    for filename in files:
        os.chown(os.path.join(fullpath, filename), uid, gid)
