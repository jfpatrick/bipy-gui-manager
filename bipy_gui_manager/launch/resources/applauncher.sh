#!/bin/bash

APP_NAME=$1
REPO_PATH=/user/bdisoft/development/python/gui/deployments
ACC_PY_PATH=/acc/local/share/python/tmp/deploy-beta/acc-py-cli/pro/bin

$ACC_PY_PATH/acc-py app run --deploy-base $REPO_PATH $APP_NAME

