PYPREFIX=`python -c "import sys;print sys.prefix;"`
sudo rm -rf ${PYPREFIX}/python2.4/site-packages/adytum/app/pymon
sudo rm -rf ${PYPREFIX}/python2.4/site-packages/PyMonitor-*.egg
sudo rm -rf build/
sudo rm -rf /usr/local/pymon
sudo rm setuptools-*.egg
sudo python setup.py install || \
    sudo python setup.py install && \
    sudo cp -p etc/example-pymon.conf /usr/local/pymon/etc/pymon.conf
