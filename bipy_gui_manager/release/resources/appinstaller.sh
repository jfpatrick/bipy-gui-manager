#!/bin/bash

APP_PATH=$1
REPO_PATH=/user/bdisoft/development/python/gui/deployments
ACC_PY_PATH=/acc/local/share/python/tmp/deploy-beta/acc-py-cli/pro/bin

# Lock dependencies
echo -e " -> Locking project's dependencies..."
if ! $ACC_PY_PATH/acc-py app lock $APP_PATH; then
    echo -e "    Locking failed! Please try running 'acc-py app lock $APP_PATH' and check the logs."
    exit 1
else

    # Apply pip workaround
    sed -i -e 's/:\/\/gitlab.cern.ch:8443/:\/\/:@gitlab.cern.ch:8443/g' $APP_PATH/deployment/app/requirements.txt 

    # Deploy to shared folder
    echo -e " -> Deploying application..."
    if ! $ACC_PY_PATH/acc-py app deploy --deploy-base $REPO_PATH $APP_PATH; then
        echo -e "    Deployment failed! Please try running 'acc-py app deploy --deploy-base $REPO_PATH $APP_PATH' and check the logs."
        exit 1
    else
        echo -e "    Deployment successful. You can now run your application with bipy-gui-manager launch $(basename $APP_PATH)."
        exit 1

    fi
fi
