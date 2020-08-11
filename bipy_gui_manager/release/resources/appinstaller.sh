#!/bin/bash

APP_NAME=$1
GIT_URL=$2
VENV_NAME="."$APP_NAME"-venv"

# Clone code
if git clone $GIT_URL $APP_NAME; then

    # Setup venvs
    deactivate
    source /acc/local/share/python/acc-py-pyqt/setup.sh

    ACCPY_WORKS=$(acc-py venv $VENV_NAME)
    if ! [[ $ACCPY_WORKS ]]; then
        echo -e " -> An error occurred activating Acc-Py. The process might fail!"
        echo -e " -> Falling back to virtualenv"
        virtualenv $VENV_NAME
    fi

    source $VENV_NAME/bin/activate
    echo -e " -> local virtualenv activated"

    # Install with pip
    echo -e " -> installing with pip..."
    if pip install ./$APP_NAME -qqq; then

       echo -e " -> pip install succeeded"
       exit 0

    else

       echo -e " -> pip install failed"
       rm -rf ./$APP_NAME
       rm -rf ./$VENV_NAME
       exit 1 

    fi

else

    echo -e " -> git clone failed"
    rm -rf ./$APP_NAME
    rm -rf ./$VENV_NAME
    exit 1

fi
