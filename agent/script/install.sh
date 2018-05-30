
curl -s -X POST -H "Content-Type: application/json" -d "{
	\"deploy_key\": \"$DEPLOY_KEY\"
}" $SERVER_URL/api/v1/agent/ > /tmp/agent.json

IP_SERVER=$(python3 -c 'import json;obj=json.load(file("/tmp/agent.json"));print (obj["ip_server"])')
IP_AGENT=$(python3 -c 'import json;obj=json.load(file("/tmp/agent.json"));print (obj["ip_agent"])')
IDENTIFIER=$(python3 -c 'import json;obj=json.load(file("/tmp/agent.json"));print (obj["identifier"])')

install_docker(){
    echo ">>>> Docker Engine Installation >>>>"
    
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo apt-get update
    sudo apt-get install -y docker-ce
    
    # (optional)
    # sudo usermod -aG docker ${USER}
    sleep 2

    echo ">>>> Docker Compose Installation >>>>"
    sudo curl -L https://github.com/docker/compose/releases/download/1.18.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose

    sleep 3
}

setup_dir(){
    echo ">>>> Initialize Directory for Sensor Purpose >>>>"

    mkdir -p $DATA_DIR/dionaea/log
    mkdir -p $DATA_DIR/dionaea/binaries
    mkdir -p $DATA_DIR/glastopf/db
    mkdir -p $DATA_DIR/glastopf/log
    mkdir -p $DATA_DIR/cowrie/log
    mkdir -p $DATA_DIR/cowrie/log/tty
    mkdir -p $DATA_DIR/cowrie/downloads
    mkdir -p $DATA_DIR/cowrie/keys

    chown -R 3500:3500 $PWD

    sleep 3
}

setup_ssh(){
    echo ">>>> Change SSH Port 22 to 2222 >>>>"
    sudo apt-get install openssh-server
    sed -i 's/Port 22/Port 2222/g' /etc/ssh/sshd_config
    service ssh restart

    sleep 3
}

setup_cronjob(){
    # Inserting Cronjob for Deleting Schedule
    crontab -l | { cat; echo "0 0 * * * bash /var/fipro/agent/script/log_deleter.sh"; } | crontab -
}

setup_fluentbit(){
    # Set Fluentbit Configuration
    sed -i 's/@SET ip_fluentd=<ip_fluentd>/@SET ip_fluentd='$IP_SERVER'/g' $DOCKER_DIR/fluentbit/conf/fluent-bit.conf
    sed -i 's/@SET ip_host=<ip_host>/@SET ip_host='$IP_AGENT'/g' $DOCKER_DIR/fluentbit/conf/fluent-bit.conf
    sed -i 's/@SET identifier=<uid>/@SET identifier='$IDENTIFIER'/g' $DOCKER_DIR/fluentbit/conf/fluent-bit.conf
}



create_user(){

}

compose(){
    docker-compose -d -f $DOCKER_DIR/docker-compose.yml up

    sleep 3

    clear
    echo ">>> Agent Installation Done <<<"
}


main(){
    install_docker
    setup_dir
    setup_ssh    
    setup_fluentbit
    setup_cronjob
    composer
}

main