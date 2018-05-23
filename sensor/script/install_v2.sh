

$SERVER_IP=''
$SENSOR_DIR=''

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

set_directory(){
    echo ">>>> Initialize Directory for Sensor Purpose >>>>"

    mkdir -p /data/dionaea/log
    mkdir -p /data/dionaea/binaries
    mkdir -p /data/glastopf/db
    mkdir -p /data/glastopf/log
    mkdir -p /data/cowrie/log
    mkdir -p /data/cowrie/log/tty
    mkdir -p /data/cowrie/downloads
    mkdir -p /data/cowrie/keys

    chown -R 3500:3500 /data

    sleep 3
}

create_user(){

}

change_ssh_service(){
    echo ">>>> Change SSH Port 22 to 2222 >>>>"
    sudo apt-get install openssh-server
    sed -i 's/Port 22/Port 2222/g' /etc/ssh/sshd_config
    service ssh restart

    sleep 3
}

clone_agent(){
    git clone https://github.com/ardikabs/fipro/sensor.git /var/fipro-agent
}

insert_cronjob(){
    # Inserting Cronjob for Deleting Schedule
}

set_fluentbit(){
    # Set Fluentbit Configuration
}

run_composer(){
    # Run Docker Compose for
        # Fluentbit-service
        # SmartAgent-service
}


main(){
    install_docker
    set_directory
    change_ssh_service
    clone_agent
    set_fluentbit
    composer
}