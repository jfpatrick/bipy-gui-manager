#!/bin/bash

# Color Escapes
NC='\033[0;m'
BOLD='\033[1;m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'


VERBOSE=$1


if [ $VERBOSE = "1" ]; then

    # Setup venvs
    echo -e "\033[0;32m=>\033[0;m Activating Acc-Py"
    source /acc/local/share/python/acc-py/base/pro/setup.sh

    echo -e "\033[0;32m=>\033[0;m Creating local virtualenv"
    acc-py venv venv

    echo -e "\033[0;32m=>\033[0;m Activating local virtualenv"
    source venv/bin/activate

    # Install with pip
    echo -e "\033[0;32m=>\033[0;m Installing your project (can take a minute)"
    if pip install -e .[all] ; then
      # Success!
      echo -e "[DEBUG] pip install succeeded"

      # Running accwidgets post-install scripts
      accwidgets-cli install-templates

      exit 0
    else
      # Failure
      echo -e "[DEBUG] pip install failed"
      exit 1
    fi

else

    # Setup venvs
    echo -e "\033[0;32m=>\033[0;m Activating Acc-Py"
    source /acc/local/share/python/acc-py/base/pro/setup.sh

    echo -e "\033[0;32m=>\033[0;m Creating local virtualenv"
    acc-py venv venv  >/dev/null 2>&1

    echo -e "\033[0;32m=>\033[0;m Activating local virtualenv"
    source venv/bin/activate

    # Install with pip
    echo -e "\033[0;32m=>\033[0;m Installing your project (can take a minute)"
    if pip install -e .[all] -qqq; then

        # Running accwidgets post-install scripts
        accwidgets-cli install-templates 2>&1
        deactivate

        # Success!
        exit 0

    else
        deactivate

        # Failed
        exit 1
    fi


fi
