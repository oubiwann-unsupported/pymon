./clean.sh
sudo python setup.py install || \
    sudo python setup.py install && \
    sudo cp -p etc/example-pymon.conf /usr/local/pymon/etc/pymon.conf
