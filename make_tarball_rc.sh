. ./make_include.sh
STAMP=`date "+%Y%m%d.%H%M%S"`
VER=`cat VERSION`
REV="pymon-${VER}-RC${1}"
DIST=./dist
mkdir $DIST
cd $DIST
DEST=$REV
mkdir $DEST
$RSYNC ../ $DEST
tar cvfj ${REV}.tar.bz2 $DEST
rm -rf $DEST

