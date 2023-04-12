#!/bin/bash

if [[ -z "${ANSIBLE_USER}" ]]; then
  read -p "Enter the Ubuntu server username: " ANSIBLE_USER
fi

if [[ -z "${ANSIBLE_PASSWORD}" ]]; then
  read -s -p "Enter the Ubuntu server password: " ANSIBLE_PASSWORD
fi

# Run the Ansible command with the user and password variables
docker run --rm -v $(pwd)/devops:/devops:ro -v $(pwd)/key:/key -v $(pwd)/src:/src:ro project-utils ansible-playbook deploy/prepare_server.yml -e "ansible_user=$ANSIBLE_USER" -e "ansible_password=$ANSIBLE_PASSWORD"
