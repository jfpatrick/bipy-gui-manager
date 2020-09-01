import os
import logging
import argparse
from pathlib import Path

from bipy_gui_manager.utils import cli as cli


def run(parameters: argparse.Namespace):

    if parameters.verbose:
        logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.DEBUG)

    # FIXME implement the multiple choice menu
    app = parameters.app

    try:
        applauncher = (Path(__file__).parent / "resources" / "app_run.sh").absolute()
        logging.debug("Execute app_run.sh")
        error = os.WEXITSTATUS(os.system(f"/bin/bash -c \"{applauncher} {app}\""))
        if error:
            cli.negative_feedback("Launch failed: {}.".format(error))
            return

    except OSError as e:
        logging.debug(e)
        cli.negative_feedback("Exiting")
        return
