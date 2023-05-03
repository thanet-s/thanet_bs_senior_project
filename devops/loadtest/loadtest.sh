#!/bin/bash

set -e # Exit if error

if [[ -z "${ANSIBLE_USER}" ]]; then
    read -p "Enter the Ubuntu server username: " ANSIBLE_USER
    export ANSIBLE_USER=$ANSIBLE_USER
fi

while true; do
    read -p "Enter a number to choose which load test script(s) to run:
0 for all
1 for monolithic
2 for loadbalance monolithic
3 for k8s monolithic
Enter your choice: " CHOICE
    if [[ $CHOICE =~ ^[0-3]$ ]]; then
        break
    else
        echo "Error: '$CHOICE' is not a valid choice. Please enter a number from 0 to 3."
    fi
done

while true; do
    read -p "Enter the number of loops to run the loadtest: " LOOPS
    if [[ $LOOPS =~ ^[0-9]+$ ]]; then
        break
    else
        echo "Error: '$LOOPS' is not a valid number. Please enter a number."
    fi
done

PROJECT_DIR=${PWD}

for ((i = 0; i < $LOOPS; i++)); do
    echo "Running loadtest $((i + 1))/$LOOPS"

    case $CHOICE in
        0) $PROJECT_DIR/devops/loadtest/loadtest_monolithic.sh
           $PROJECT_DIR/devops/loadtest/loadtest_loadbalance_monolithic.sh
           $PROJECT_DIR/devops/loadtest/loadtest_k8s_monolithic.sh;;
        1) $PROJECT_DIR/devops/loadtest/loadtest_monolithic.sh;;
        2) $PROJECT_DIR/devops/loadtest/loadtest_loadbalance_monolithic.sh;;
        3) $PROJECT_DIR/devops/loadtest/loadtest_k8s_monolithic.sh;;
    esac

    echo "Loop $((i + 1)) complete"
done

echo Loadtest complete!
