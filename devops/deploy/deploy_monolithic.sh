#!/bin/bash

if [[ -z "${ANSIBLE_USER}" ]]; then
  read -p "Enter the Ubuntu server username: " ANSIBLE_USER
fi

# Run the Ansible command with the user variable
docker run --rm -v $(pwd)/devops:/devops:ro -v $(pwd)/key:/key:ro project-utils ansible-playbook deploy/deploy_monolithic.yml -e "ansible_user=$ANSIBLE_USER"
