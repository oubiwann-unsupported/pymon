svn stat|egrep -v '.swp|.pyc|lib/os|lib/net'
svn stat lib/os|egrep -v '.swp|.pyc'
svn stat lib/net|egrep -v '.swp|.pyc'
