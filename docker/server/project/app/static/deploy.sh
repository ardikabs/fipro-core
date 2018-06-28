#!/bin/bash

if [[ "$(whoami)" != "root" ]]; then
	echo "You must be root to run this script"
	exit 1
fi

if [[ $# -ne 3 ]]; then
	echo "Wrong number of arguments supplied"
	echo "Usage: $0 <server_url> <api_key> <deploy_key>"
	exit 1
fi

BASE_DIR=`dirname "$(readlink -f "$0")"`
SERVER_URL=$1
API_KEY=$2
DEPLOY_KEY=$3
IPADDR=$(hostname -I | cut -d ' ' -f1)

sudo apt-get -y update
sudo apt-get install -y git curl

curl -s -X POST -H "Content-Type: application/json" -d "{
	\"deploy_key\": \"$DEPLOY_KEY\",
    \"api_key\": \"$API_KEY\",
	\"ipaddr\": \"$IPADDR\"
}" $SERVER_URL/api/v1/agent/ > /tmp/agent.json

STATUS=$(cat /tmp/agent.json | python3 -c 'import sys,json;obj=json.load(sys.stdin);print (obj["status"])')

if [[ "$STATUS" != True ]]; then
	MSG=$(cat /tmp/agent.json | python3 -c 'import sys,json;obj=json.load(sys.stdin);print (obj["message"])')
    clear
    echo -e "\n\n>>> Deploy Key Error"
	echo -e ">>> $MSG"
    echo -e "##### Installer Stopped #####\n\n\n"
    exit 1
fi

SERVER_IP=$(cat /tmp/agent.json | python3 -c 'import sys,json;obj=json.load(sys.stdin);print (obj["server_ip"])')
AGENT_IP=$(cat /tmp/agent.json | python3 -c 'import sys,json;obj=json.load(sys.stdin);print (obj["agent_ip"])')
IDENTIFIER=$(cat /tmp/agent.json | python3 -c 'import sys,json;obj=json.load(sys.stdin);print (obj["identifier"])')


############################################## AGENT SECTION ########################################################

mkdir -p /var/fipro/agent

git clone https://github.com/ardikabs/fipro-agent.git /var/fipro/agent

cd /var/fipro/agent

SCRIPT_DIR=$PWD/script
DOCKER_DIR=$PWD/docker
DATA_DIR=$PWD/data

chmod +x $SCRIPT_DIR/install.sh

sudo $SCRIPT_DIR/install.sh $SERVER_IP $AGENT_IP $IDENTIFIER
