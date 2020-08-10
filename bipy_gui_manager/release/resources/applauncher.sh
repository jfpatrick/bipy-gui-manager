APP_NAME=$1
VENV="."$APP_NAME"-venv"

# Setup venvs
source /acc/local/share/python/acc-py-pyqt/setup.sh
source /user/bdisoft/development/python/gui/expert/$VENV/bin/activate

# Launch app
$APP_NAME

