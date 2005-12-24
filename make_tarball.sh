. ./make_include.sh
VER=`cat VERSION`
REV="pymon-${VER}"
DIST=./dist
mkdir $DIST
cd $DIST
DEST=$REV
mkdir $DEST
$RSYNC \
../ $DEST
tar cvfj ${REV}.tar.bz2 $DEST
rm -rf $DEST

