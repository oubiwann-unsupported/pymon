if [ ! -x ./docs/api ]; then
  mkdir -p ./docs/api
fi
svn rm docs/api --force
epydoc -o ./docs/api/ ./
svn add docs/api
svn commit
