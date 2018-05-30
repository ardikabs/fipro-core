#!/bin/bash
BUILD_PKGS="autoconf automake build-essential check cython3 libcurl4-openssl-dev libemu-dev libev-dev libglib2.0-dev libloudmouth1-dev libnetfilter-queue-dev libpcap-dev libssl-dev libtool libudns-dev python3-dev git"

RUN_PKGS="ca-certificates python3 python3-yaml supervisor"
LIB_PKGS="libcurl3 libemu2 libev4 libglib2.0-0 libnetfilter-queue1 libpcap0.8 libpython3.5 libudns0"

apt-get update
apt-get install -y --no-install-recommends $BUILD_PKGS $RUN_PKGS

git clone https://github.com/DinoTools/dionaea /root/dionaea/
cd /root/dionaea
autoreconf -vi
./configure \
    --prefix=/opt/dionaea \
    --with-python=/usr/bin/python3 \
    --with-cython-dir=/usr/bin \
    --enable-ev \
    --with-ev-include=/usr/include \
    --with-ev-lib=/usr/lib \
    --with-emu-lib=/usr/lib/libemu \
    --with-emu-include=/usr/include \
    --with-nl-include=/usr/include/libnl3 \
    --with-nl-lib=/usr/lib \
    --enable-static
make
make install

apt-get purge -y $BUILD_PKGS
apt-get autoremove --purge -y
apt-get install -y $RUN_PKGS $LIB_PKGS
apt-get clean
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*   
