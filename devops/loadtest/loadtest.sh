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
4 for k8s microservice
Enter your choice: " CHOICE
    if [[ $CHOICE =~ ^[0-4]$ ]]; then
        break
    else
        echo "Error: '$CHOICE' is not a valid choice. Please enter a number from 0 to 4."
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
    0)
        $PROJECT_DIR/devops/loadtest/loadtest_monolithic.sh
        $PROJECT_DIR/devops/loadtest/loadtest_loadbalance_monolithic.sh
        $PROJECT_DIR/devops/loadtest/loadtest_k8s_monolithic.sh
        $PROJECT_DIR/devops/loadtest/loadtest_k8s_microservice.sh
        ;;
    1) $PROJECT_DIR/devops/loadtest/loadtest_monolithic.sh ;;
    2) $PROJECT_DIR/devops/loadtest/loadtest_loadbalance_monolithic.sh ;;
    3) $PROJECT_DIR/devops/loadtest/loadtest_k8s_monolithic.sh ;;
    4) $PROJECT_DIR/devops/loadtest/loadtest_k8s_microservice.sh ;;
    esac

    echo "Loop $((i + 1)) complete"
done

if [[ $CHOICE == 0 ]]; then
    echo ""
    echo "++++++++++++++ Run Summary Script ++++++++++++++"
    #Loadtest Summary
    docker run --rm -v $(pwd)/devops/loadtest/summary_loadtest.py:/app/summary_loadtest.py -v $(pwd)/loadtest_result:/app/loadtest_result:ro python:3.11-slim python /app/summary_loadtest.py
fi

echo Loadtest complete!
