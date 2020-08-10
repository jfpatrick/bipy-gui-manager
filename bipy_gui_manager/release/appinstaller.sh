APP_NAME=$1
GIT_URL=$2
VENV_NAME="."$APP_NAME"-venv"

# Setup venvs
source /acc/local/share/python/acc-py-pyqt/setup.sh
acc-py venv $VENV_NAME
source $VENV_NAME/bin/activate

# Install with pip
if git clone $GIT_URL $APP_NAME; then
    if pip install ./$APP_NAME ; then

       echo -e " -> pip install succeeded"
       exit 0

    else

       echo -e " -> pip install failed"
       rm -r ./$APP_NAME
       rm -rf ./$VENV_NAME
       exit 1 

    fi

else

    echo -e " -> git clone failed"
    rm -r ./$APP_NAME
    rm -rf ./$VENV_NAME
    exit 1

fi
