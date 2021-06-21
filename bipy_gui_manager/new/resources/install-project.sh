#!/bin/bash

# Color Escapes
NC='\033[0;m'
BOLD='\033[1;m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'

TYPE=$1
VERBOSE=$2


# Setup venvs
echo -e "\033[0;32m=>\033[0;m Activating Acc-Py"
source /acc/local/share/python/acc-py/base/pro/setup.sh

echo -e "\033[0;32m=>\033[0;m Creating local virtualenv"
acc-py venv venv

echo -e "\033[0;32m=>\033[0;m Activating local virtualenv"
source venv/bin/activate

# Install with pip
echo -e "\033[0;32m=>\033[0;m Installing your project (can take a minute)"

if [ $TYPE = "comrad" ]; then

  if [ $VERBOSE = "1" ]; then

    # Install ComRAD Project - verbose
    if pip install comrad ; then
      echo -e "[DEBUG] pip install succeeded"
      exit 0
    else
      echo -e "[DEBUG] pip install failed"
      exit 1
    fi

  else

    # Install ComRAD Project - quiet
    if pip install comrad ; then
      exit 0
    else
      exit 1
    fi

  fi

else

  if [ $VERBOSE = "1" ]; then

    # Install PyQt Project - verbose
    if pip install -e .[all] ; then

      echo -e "[DEBUG] pip install succeeded"
      accwidgets-cli install-templates     # Running accwidgets post-install scripts
      exit 0

    else
      echo -e "[DEBUG] pip install failed"
      exit 1
    fi

  else

    # Install PyQt Project - quiet
    if pip install -e .[all] -qqq; then

        # Running accwidgets post-install scripts
        accwidgets-cli install-templates 2>&1
        deactivate
        exit 0

    else
        deactivate
        exit 1
    fi

  fi

fi

