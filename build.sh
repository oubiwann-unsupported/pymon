sudo rm -rf /System/Library/Frameworks/Python.framework/Versions/2.3/lib/python2.3/site-packages/adytum/app/pymon
sudo rm -rf build/
chmod -R 777 data
sudo python setup.py install
sudo cp -p /usr/local/pymon/conf/example-pymon.xml /usr/local/pymon/conf/pymon.xml
