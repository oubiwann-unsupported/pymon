STAMP=`date "+%Y%m%d.%H%M%S"`
VER=`cat VERSION`
REV="pymon-${VER}-dev-${STAMP}"
DIST=./dist
mkdir $DIST
cd $DIST
DEST=$REV
mkdir $DEST
rsync \
--exclude="*.pyc" \
--exclude="*.sh" \
--exclude="*.swp" \
--exclude=".svn" \
--exclude="build*" \
--exclude="contrib*" \
--exclude="dist" \
--exclude="docs" \
--exclude="etc/old" \
--exclude="etc/pymon.conf" \
--exclude="make*" \
--exclude="PyMonitor.egg-info" \
--exclude="releases" \
--exclude="ResourceFiles" \
--exclude="sandbox" \
--exclude="Session.vim" \
--exclude="sourceforge_website" \
--exclude="svnstat.sh" \
--exclude="temp*" \
--exclude="test*" \
--exclude="twistd.pid" \
--recursive \
--links \
--times \
--perms \
--delete \
--delete-after \
--force \
--stats \
../ $DEST
mv $DEST/setup_pymon.py $DEST/setup.py
tar cvfj ${REV}.tar.bz2 $DEST
rm -rf $DEST

