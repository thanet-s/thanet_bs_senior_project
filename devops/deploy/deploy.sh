#!/bin/bash

set -e # Exit if error

if [[ -z "${ANSIBLE_USER}" ]]; then
  read -p "Enter the Ubuntu server username: " ANSIBLE_USER
  export ANSIBLE_USER=$ANSIBLE_USER
fi

if [[ -z "${ANSIBLE_PASSWORD}" ]]; then
  read -s -p "Enter the Ubuntu server password: " ANSIBLE_PASSWORD
  export ANSIBLE_PASSWORD=$ANSIBLE_PASSWORD
fi

PROJECT_DIR=${PWD}

# Run prepare script
$PROJECT_DIR/devops/deploy/prepare_server.sh

# Setup Group 1
$PROJECT_DIR/devops/deploy/deploy_monolithic.sh

# Setup Group 2
$PROJECT_DIR/devops/deploy/deploy_loadbalance_monolithic.sh

# Setup Group 3
$PROJECT_DIR/devops/deploy/deploy_kubernetes.sh

echo Deployment success!
