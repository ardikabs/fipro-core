#!/bin/bash
SCRIPT_DIR=`dirname "$(readlink -f "$0")"`
SERVER_DIR=`dirname "$(readlink -f $SCRIPT_DIR)"`
DOCKER_DIR=$SERVER_DIR/docker
install_docker(){
    echo -e "\n\n>>>> Docker Engine Installation >>>>"
    
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    sudo apt-get update
    sudo apt-get install -y docker-ce
    
    # (optional)
    sudo usermod -aG docker fipro
    sleep 2

    echo ">>>> Docker Compose Installation >>>>"
    curl -L https://github.com/docker/compose/releases/download/1.18.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose

    sleep 3
}

setup_collector(){
    COLLECTOR_DIR=$DOCKER_DIR/mqtt-subs/collector
    touch $COLLECTOR_DIR/.env
    
    echo "USERNAME_MQTT=mycollector" >> $COLLECTOR_DIR/.env
    echo "PASSWD_MQTT=rustygear125" >> $COLLECTOR_DIR/.env
}

setup_webserver(){
    WEB_DIR=$DOCKER_DIR/web/project
    touch $WEB_DIR/.env

    APP_NAME=FIPRO
    APP_SETTINGS=development
    SECRET_KEY=b'159216c9eb4cd34e5b093d95ec9f8245d3a56b6a1c09d071'
    MONGODB_URL=mongodb://192.168.1.100:27017/
    echo "APP_NAME=FIPRO SERVER" >> $COLLECTOR_DIR/.env
    echo "APP_SETTINGS=development" >> $COLLECTOR_DIR/.env
    echo "SECRET_KEY=$(python3 -c 'import os;import binascii;print(binascii.hexlify(os.urandom(24)))')"
}

add_sudoers(){
    while [[ -n $1 ]]; do
        echo "$1 ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers;
        shift
    done
}

create_user(){
    sudo addgroup --gid 3500 fipro
    sudo adduser --system --shell /bin/bash --uid 3500 --disabled-password \
        --disabled-login --gid 3500 fipro
    
    add_sudoers fipro
}

composer(){
    sudo -u fipro docker-compose -f $DOCKER_DIR/docker-compose.yml up -d
    sleep 3
    clear
    echo "\n\n>>> Server Installation Done <<<"
}

main(){
    create_user
    install_docker
    setup_collector
    setup_webserver
    composer
}
main