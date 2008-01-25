STAMP=`date "+%Y%m%d.%H%M%S"`
VER=`cat VERSION`
REV="pymon-${VER}-dev-${STAMP}"
DIST=./dist
mkdir $DIST
cd $DIST
DEST=$REV
mkdir $DEST
$RSYNC \
../ $DEST
tar cvfj ${REV}.tar.bz2 $DEST
rm -rf $DEST

