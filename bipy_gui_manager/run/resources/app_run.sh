#!/bin/bash

APP_NAME=$1
REPO_PATH=$2
ACC_PY_PATH=$3

$ACC_PY_PATH/acc-py app run --deploy-base $REPO_PATH $APP_NAME

