if [ ! -x ./docs/api ]; then
  mkdir -p ./docs/api
fi
# get rid of compiled python files
find ./ -name "*.pyc" -exec rm -f {} \;
# start with a fresh set of database files
find /tmp -name "pymon.*" -exec rm -f {} \;
# get rid of the auto-generated docs and add the new ones
svn rm docs/api --force
epydoc -o ./docs/api/ ./
svn add docs/api
# commit the changes
svn commit
