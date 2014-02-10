#!/usr/bin/env bash

sudo apt-get update
sudo apt-get install make -y
sudo apt-get install patch -y
#Gets and installs Apache Web Server
sudo apt-get install -y apache2
rm -rf /var/www
ln -fs /vagrant /var/www

sudo su -
cd /home/vagrant
#Imports SQLite 3.5.9 from shared folder (/var/www) and installs it
wget http://localhost/sqlite-3.5.9.tar.gz
tar xzvf sqlite-3.5.9.tar.gz
mkdir bld
cd bld
../sqlite-3.5.9/configure
make
make install
cd ..
#Imports Python 2.6.8 from shared folder (/var/www) and installs it
#The patches (setup_py.patch, ssl.patch, & ssl_py.patch) used to make Python 2.6.8 work,
#are published at http://ubuntuforums.org/showthread.php?t=1976837 by appociappo
apt-get build-dep python -y
wget http://localhost/Python-2.6.8.tar.gz
tar xzvf Python-2.6.8.tar.gz
cd Python-2.6.8
cp /var/www/setup_py.patch setup_py.patch
patch setup_py.patch < setup_py.patch
cp /var/www/ssl.patch ssl.patch
patch Modules/_ssl.c < ssl.patch
export arch=$(dpkg-architecture -qDEB_HOST_MULTIARCH)
export LDFLAGS="-L/usr/lib/$arch -L/lib/$arch"
export CFLAGS="-I/usr/include/$arch"
export CPPFLAGS="-I/usr/include/$arch"
./configure
cp /var/www/ssl_py.patch ssl_py.patch
patch Lib/ssl.py < ssl_py.patch
make MACHDEP=linux2 -j3
make install
cd ..
#Imports Django 1.6 form shared folder (/var/www) and installs it
wget http://localhost/Django-1.6.tar.gz
tar xzvf Django-1.6.tar.gz
cd Django-1.6
python setup.py install
