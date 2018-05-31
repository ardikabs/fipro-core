
if [[ "$(whoami)" != "root" ]]; then
	echo "You must be root to run this script"
	exit 1
fi

if [[ $# -ne 3 ]]; then
	echo "Wrong number of arguments supplied"
	echo "Usage: $0 <server_url> <api_key> <deploy_key>"
	exit 1
fi

CURRENT_DIR=`dirname "$(readlink -f "$0")"`
SERVER_URL=$1
API_KEY=$2
DEPLOY_KEY=$3

sudo apt-get update
sudo apt-get install git curl dig

mkdir -p /var/fipro/agent

git clone https://github.com/ardikabs/fipro/agent.git /var/fipro/agent

cd /var/fipro/agent

SCRIPT_DIR=$PWD/script
DOCKER_DIR=$PWD/docker
DATA_DIR=$PWD/data

chmod +x $SCRIPT_DIR/install.sh

sudo ./install.sh
