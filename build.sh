PYPREFIX=`python -c "import sys;print sys.prefix;"`
sudo rm -rf ${PYPREFIX}/python2.3/site-packages/adytum/app/pymon
sudo rm -rf build/
sudo rm -rf /usr/local/pymon
chmod -R 777 data
sudo python setup.py install
sudo cp -p conf/template-pymon.xml /usr/local/pymon/conf/pymon.xml