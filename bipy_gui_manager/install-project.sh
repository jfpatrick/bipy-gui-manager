# Color Escapes
NC='\033[0;m'
BOLD='\033[1;m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'

# Setup venvs
echo -e "    - Activating Acc-Py"
source /acc/local/share/python/acc-py-pyqt/setup.sh  >/dev/null 2>&1
echo -e "    - Creating local virtualenv"
acc-py venv venv  >/dev/null 2>&1

source venv/bin/activate
echo -e "    - Activating local virtualenv"

# Install with pip
echo -e "    - Installing (can take a minute - please ignore requirements errors)"
if pip install -e . -qqq; then
  # Success!
  exit 0
else
  # Failure
  exit 1
fi

# Go back to the dir we started from
cd ../