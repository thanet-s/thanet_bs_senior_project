#!/bin/bash

set -e # Exit if error

if [[ -z "${ANSIBLE_USER}" ]]; then
  read -p "Enter the Ubuntu server username: " ANSIBLE_USER
fi

# Pre setup cluster
docker run --rm -v $(pwd)/devops:/devops -v $(pwd)/key:/key:ro project-utils ansible-playbook deploy/deploy_kubernetes_precluster.yml -e "ansible_user=$ANSIBLE_USER"

# Setup k8s cluster
docker run --rm --mount type=bind,source="$(pwd)"/devops/deploy/kubespray/inventory/ubu-cluster,dst=/inventory -v $(pwd)/key:/key:ro kubespray ansible-playbook cluster.yml -i /inventory/inventory.ini -e "ansible_user=$ANSIBLE_USER" --become --become-user=root

# Post setup cluster
docker run --rm -v $(pwd)/devops:/devops:ro -v $(pwd)/key:/key:ro project-utils ansible-playbook deploy/deploy_kubernetes_postcluster.yml -e "ansible_user=$ANSIBLE_USER"

# Shutdown group 3 VMs
docker run --rm -v $(pwd)/devops:/devops:ro -v $(pwd)/key:/key:ro project-utils ansible-playbook /devops/vm_group_switch.yml -e "ansible_user=$ANSIBLE_USER group_name=vm_group3 vm_action=shutdown"
