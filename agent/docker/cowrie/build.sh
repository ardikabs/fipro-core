#!/bin/bash

apk -U upgrade
apk add git procps py-pip mpfr-dev openssl-dev mpc1-dev libffi-dev build-base python python-dev py-mysqldb py-setuptools gmp-dev

addgroup -g 3500 cowrie
adduser -S -H -u 3500 -D -g 3500 cowrie

git clone https://github.com/micheloosterhof/cowrie.git /home/cowrie/cowrie/
cd /home/cowrie/cowrie
pip install --no-cache-dir --upgrade cffi
pip install --no-cache-dir -U -r requirements.txt

cp /root/dist/cowrie.cfg /home/cowrie/cowrie/cowrie.cfg
cp /root/dist/userdb.txt /home/cowrie/cowrie/data/userdb.txt
chown cowrie:cowrie -R /home/cowrie/*

apk del git py-pip mpfr-dev mpc1-dev libffi-dev build-base py-mysqldb gmp-dev python-dev
rm -rf /var/cache/apk/*

