./make_tarball_rc.sh $1
LATEST=`ls -rt dist/*.bz2|grep RC|tail -1`
mv $LATEST releases
NEW=`svn stat releases|egrep -e '^\?'|awk '{print $2}'`
for FILE in $NEW
    do
    svn add $FILE
    done
svn commit releases -m "Automated development release."
