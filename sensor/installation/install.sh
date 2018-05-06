
function create_users {
    # Services dijalankan dengan tidak menggunakan user root
    addgroup --gid 3500 sensor
    adduser --system --shell /bin/bash --uid 3500 --disabled-password --gid 3500 sensor 

    sudo apt-get update
    sudo apt-get install curl git python3-pip
}

function init_docker_services {
    echo '>>>>>> Installation Process of Docker Services \n<<<<<<'
    
    # Docker Engine
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo apt-get update
    sudo apt-get install -y docker-ce

    # Docker Compose
    curl -L https://github.com/docker/compose/releases/download/1.18.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose

    sleep 3
    # Restart SSH Service after change SSH Port 22 to 2222
    restart_ssh_service
}

function init_directory_set {
    echo '>>>>>> Initialize Directory for Sensor Data \n<<<<<<'

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

function init_web_service {
    # Running Web Service on Container
    git https://github.com/ardikabs/fipro/sensor.git ~/sensor
    cd ~/sensor
    sleep 1

    pip install virtualenv
    virtualenv -p `which python3` venv
    source ./venv/bin/activate
    pip install -r requirements.txt

    if [ -e .env ]; then
        rm .env
    fi
    touch .env
    echo 'APP_NAME=Sensor-Side Web Service' >> .env
    echo 'APP_SETTINGS=development' >> .env
    echo 'SECRET_KEY=@!sensor-side-ku-yang_paling-oke-123' >> .env

    screen -d -m -S sensor_ws bash 'python3 manage.py runserver'
    sleep 3
}

function check_status {
    # Check Status for All Services

    echo '>>>> All Services are ready to go <<<<<<'
}
function restart_ssh_service {
    echo '>>>>>> Change SSH Port 22 to 2222 <<<<<<<<'
    sudo apt-get install openssh-server
    sed -i 's/Port 22/Port 2222/g' /etc/ssh/sshd_config
    service ssh restart
    sleep 3
}



function main {
    create_users
    init_docker_services
    init_directory_set
    init_web_service
    
    check_status
}


main