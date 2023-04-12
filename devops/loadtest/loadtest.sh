#!/bin/bash

set -e # Exit if error

if [[ -z "${ANSIBLE_USER}" ]]; then
    read -p "Enter the Ubuntu server username: " ANSIBLE_USER
    export ANSIBLE_USER=$ANSIBLE_USER
fi

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

    # Run loadtest script
    $PROJECT_DIR/devops/loadtest/loadtest_monolithic.sh
    $PROJECT_DIR/devops/loadtest/loadtest_loadbalance_monolithic.sh

    echo "Loop $((i + 1)) complete"
done

echo Loadtest complete!
