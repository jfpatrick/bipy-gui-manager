#!/bin/bash

# Color Escapes
NC='\033[0;m'
BOLD='\033[1;m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'

# Setup venvs
echo -e "[DEBUG] Activating Acc-Py"
source /acc/local/share/python/acc-py-pyqt/setup.sh
echo -e "[DEBUG] Creating local virtualenv"
acc-py venv venv

echo -e "\033[0;32m=>\033[0;m Activating local virtualenv"
source venv/bin/activate

# Install with pip
echo -e "\033[0;32m=>\033[0;m Installing (can take a minute - PLEASE IGNORE ACC-PY REQUIREMENTS ERRORS)"
if pip install -e .[all] ; then
  # Success!
  echo -e "[DEBUG] pip install succeeded"
  exit 0
else
  # Failure
  echo -e "[DEBUG] pip install failed"
  exit 1
fi
