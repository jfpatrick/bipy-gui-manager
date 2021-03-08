#!/bin/bash

APP_PATH=$1
REPO_PATH=$2
ACC_PY_PATH=$3
VERBOSE=$4


if [ $VERBOSE = "1" ]; then

    # Apply pip workaround
    echo -e "-> Apply pip workaround"
    sed -i -e 's/:\/\/gitlab.cern.ch:8443/:\/\/:@gitlab.cern.ch:8443/g' $APP_PATH/deployment/app/requirements.txt

    # Deploy to shared folder
    echo -e "-> Deploying application (can take a few minutes)..."
    if ! $ACC_PY_PATH/acc-py app deploy --deploy-base $REPO_PATH $APP_PATH; then
        echo -e "   Deployment failed! Please try running 'acc-py app deploy --deploy-base $REPO_PATH $APP_PATH' and check the logs."
        echo -e "   If you are deploying a new version, make sure you increased the version number (re-deploy is not allowed)"
        exit 1
    else
        echo -e "   Deployment successful. You can now run your application with bipy-gui-manager run $(basename $APP_PATH)."
        exit 0

    fi

else

    # Apply pip workaround
    sed -i -e 's/:\/\/gitlab.cern.ch:8443/:\/\/:@gitlab.cern.ch:8443/g' $APP_PATH/deployment/app/requirements.txt

    # Deploy to shared folder
    echo -e "-> Deploying application (can take a few minutes)..."
    if ! $ACC_PY_PATH/acc-py app deploy --deploy-base $REPO_PATH $APP_PATH &> /dev/null; then
        echo -e "   Deployment failed! Please try running 'acc-py app deploy --deploy-base $REPO_PATH $APP_PATH' and check the logs."
        echo -e "   If you are deploying a new version, make sure you increased the version number (re-deploy is not allowed)"
        exit 1
    else
        echo -e "   Deployment successful. You can now run your application with bipy-gui-manager run $(basename $APP_PATH)."
        exit 0

    fi
fi
