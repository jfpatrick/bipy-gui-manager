#!/bin/bash

APP_PATH=$1
REPO_PATH=$2
ACC_PY_PATH=$3
TYPE=$4
VERBOSE=$5


# Deploy as PyQt
if [ $TYPE = "pyqt" ]; then

    # Apply pip workaround
    if [ $VERBOSE = "1" ]; then
        echo -e "-> Apply pip workaround"
    fi
    sed -i -e 's/:\/\/gitlab.cern.ch:8443/:\/\/:@gitlab.cern.ch:8443/g' $APP_PATH/deployment/app/requirements.txt

    if [ $VERBOSE = "1" ]; then

        # Deploy to shared folder
        echo -e "-> Deploying application (can take a few minutes)..."
        if ! $ACC_PY_PATH/acc-py app lock $APP_PATH; then
            echo -e "   Dependency lock failed! Please try running 'acc-py app lock $APP_PATH' and check the logs."
            exit 1
        else
            if ! $ACC_PY_PATH/acc-py app deploy --deploy-base $REPO_PATH $APP_PATH; then
                echo -e "   Deployment failed! Please try running 'acc-py app deploy --deploy-base $REPO_PATH $APP_PATH' and check the logs."
                echo -e "   If you are deploying a new version, make sure you increased the version number (re-deploy is not allowed)"
                exit 1
            else
                echo -e "   Deployment successful. You can now run your application with bipy-gui-manager run $(basename $APP_PATH)."
                exit 0
            fi
        fi

    else

        # Deploy to shared folder
        echo -e "-> Deploying application (can take a few minutes)..."
        if ! $ACC_PY_PATH/acc-py app lock $APP_PATH &> /dev/null; then
            echo -e "   Dependency lock failed! Please try running 'acc-py app lock $APP_PATH' and check the logs."
            exit 1
        else
            if ! $ACC_PY_PATH/acc-py app deploy --deploy-base $REPO_PATH $APP_PATH &> /dev/null; then
                echo -e "   Deployment failed! Please try running 'acc-py app deploy --deploy-base $REPO_PATH $APP_PATH' and check the logs."
                echo -e "   If you are deploying a new version, make sure you increased the version number (re-deploy is not allowed)"
                exit 1
            else
                echo -e "   Deployment successful. You can now run your application with bipy-gui-manager run $(basename $APP_PATH)."
                exit 0

            fi
        fi
    fi

# Deploy as ComRAD
else

    if ! comrad package app/main.py ; then
        echo -e "   Failed to launch 'comrad package'. Make sure your virtualenv is active before proceeding and that you have ComRAD installed."
        exit 1
    fi

    echo -e "\nDeploying application..."
    echo -e "-> NOTE: This step may take several minutes.\n"

    if [ $VERBOSE = "1" ]; then

        if ! pip wheel -w $APP_PATH/app --no-deps $APP_PATH/app ; then
            echo -e "   Wheel generation failed! Check the logs above for errors."
            exit 1
        else
            if ! $ACC_PY_PATH/acc-py app deploy --deploy-base $REPO_PATH $APP_PATH/app/*.whl; then
                echo -e "   Deployment failed! Check the logs above for errors."
                echo -e "   If you are deploying a new version, make sure you increased the version number (re-deploy is not allowed)"
                echo -e "   If you have many .whl files, try deleting them all and repeating this command."
                exit 1
            else
                rm $APP_PATH/app/*.whl
                echo -e "   Deployment successful. You can now run your application with bipy-gui-manager run $(basename $APP_PATH)."
                exit 0
            fi
        fi

    else

        if ! pip wheel -w $APP_PATH/app --no-deps $APP_PATH/app/ &>/dev/null ; then
            echo -e "   Wheel generation failed! Please try running 'pip wheel -w $APP_PATH/app --no-deps $APP_PATH/app' and check the logs."
            exit 1
        else
            if ! $ACC_PY_PATH/acc-py app deploy --deploy-base $REPO_PATH $APP_PATH/app/*.whl &>/dev/null; then
                echo -e "   Deployment failed! Please try running 'acc-py app deploy --deploy-base $REPO_PATH $APP_PATH/app/*.whl' and check the logs."
                echo -e "   If you are deploying a new version, make sure you increased the version number (re-deploy is not allowed)"
                echo -e "   If you have many .whl files, try deleting them all and repeating this command."
                exit 1
            else
                rm $APP_PATH/app/*.whl
                echo -e "   Deployment successful. You can now run your application with bipy-gui-manager run $(basename $APP_PATH)."
                exit 0
            fi
        fi

    fi

fi
