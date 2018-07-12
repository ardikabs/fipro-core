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

    # Environment variable for Collector
    touch $COLLECTOR_DIR/.env
    
    echo "USERNAME_MQTT=mycollector" >> $COLLECTOR_DIR/.env
    echo "PASSWD_MQTT=rustygear125" >> $COLLECTOR_DIR/.env
}

setup_webserver(){
    WEB_DIR=$DOCKER_DIR/web/project 

    # Environment variable for Web Server
    touch $WEB_DIR/.env

    echo "APP_NAME=FIPRO" >> $WEB_DIR/.env
    echo "APP_SETTINGS=development" >> $WEB_DIR/.env
    echo "SECRET_KEY=$(python3 -c 'import os;import binascii;print(binascii.hexlify(os.urandom(24)))')" >> $WEB_DIR/.env
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
    
    # Environment variable for Docker Compose
    touch $DOCKER_DIR/.env
    echo "SERVER_DIR=$SERVER_DIR" >> $DOCKER_DIR/.env

    sudo -u fipro docker-compose -f $DOCKER_DIR/docker-compose.yml up -d
    sleep 3
    clear
    echo -e "\n\n>>> Server Installation Done <<<"
}

main(){
    create_user
    install_docker
    setup_collector
    setup_webserver
    composer
}
main