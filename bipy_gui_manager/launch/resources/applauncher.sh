#!/bin/bash

APP_NAME=$1
DEPLOY_FOLDER=$2
VENV="."$APP_NAME"-venv"

# Setup venvs
source /acc/local/share/python/acc-py-pyqt/setup.sh
source $DEPLOY_FOLDER/$VENV/bin/activate

# Launch app
$APP_NAME

