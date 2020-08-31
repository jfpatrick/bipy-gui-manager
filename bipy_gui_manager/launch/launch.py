import os
import logging
import argparse
from pathlib import Path

from bipy_gui_manager.utils import cli as cli
from bipy_gui_manager.release.release import DEPLOY_FOLDER, DEPLOY_FOLDER_DEBUG


def launch(parameters: argparse.Namespace):

    if parameters.verbose or parameters.debug:
        logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.DEBUG)

    # deploy_folder: Path
    # if parameters.debug:
    #     os.makedirs(DEPLOY_FOLDER_DEBUG, exist_ok=True)
    #     deploy_folder = Path(DEPLOY_FOLDER_DEBUG)
    # else:
    #     deploy_folder = Path(DEPLOY_FOLDER)

    # FIXME implement the multiple choice menu
    app = parameters.app

    try:
        applauncher = (Path(__file__).parent / "resources" / "applauncher.sh").absolute()
        logging.debug("Execute applauncher.sh")
        error = os.WEXITSTATUS(os.system(f"/bin/bash -c \"{applauncher} {app}\""))
        if error:
            cli.negative_feedback("Launch failed: {}.".format(error))
            return

    except OSError as e:
        logging.debug(e)
        cli.negative_feedback("Exiting")
        return
