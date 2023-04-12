#!/bin/bash

set -e # Exit if error

if [[ -z "${ANSIBLE_USER}" ]]; then
    read -p "Enter the Ubuntu server username: " ANSIBLE_USER
fi

# Start group 1 VMs
docker run --rm -v $(pwd)/devops:/devops:ro -v $(pwd)/key:/key:ro project-utils ansible-playbook /devops/vm_group_switch.yml -e "ansible_user=$ANSIBLE_USER group_name=vm_group1 vm_action=start"

# Run the Ansible playbook
docker run --rm -v $(pwd)/devops:/devops:ro -v $(pwd)/key:/key:ro -v $(pwd)/loadtest_result:/loadtest_result project-utils ansible-playbook loadtest/loadtest_monolithic.yml -e "ansible_user=$ANSIBLE_USER"

# Shutdown group 1 VMs
docker run --rm -v $(pwd)/devops:/devops:ro -v $(pwd)/key:/key:ro project-utils ansible-playbook /devops/vm_group_switch.yml -e "ansible_user=$ANSIBLE_USER group_name=vm_group1 vm_action=shutdown"
