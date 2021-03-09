import os
import logging
import argparse
from pathlib import Path

from bipy_gui_manager import OPERATIONAL_DEPLOY_PATH, DEVELOPMENT_DEPLOY_PATH, ACC_PY_PATH
from bipy_gui_manager.utils import cli as cli


APP_RUN_SCRIPT = (Path(__file__).parent / "resources" / "app_run.sh").absolute()


def run(parameters: argparse.Namespace):

    if parameters.verbose:
        logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.DEBUG)

    # FIXME implement the multiple choice menu
    app = parameters.app
    if not app:
        cli.negative_feedback("Please specify the name of the application to run. "
                              "Remember that it must be deployed before it can be run with this command.")
        return

    repo_path = OPERATIONAL_DEPLOY_PATH if parameters.operational else DEVELOPMENT_DEPLOY_PATH

    try:
        logging.debug("Execute app_run.sh")
        error = os.WEXITSTATUS(os.system(f"/bin/bash -c \"{APP_RUN_SCRIPT} {app} {repo_path} {ACC_PY_PATH}\""))
        if error:
            cli.negative_feedback("Launch failed: {}.".format(error))
            return

    except OSError as e:
        logging.debug(e)
        cli.negative_feedback("Exiting")
        return


def get_runnable_apps_for_argcomplete():
    """ Returns a list of all the app names found under BOTH the dev and ops deploy paths (for argcomplete) """
    ops_apps = [os.path.basename(app) for app in Path(OPERATIONAL_DEPLOY_PATH).iterdir() if os.path.isdir(app)]
    dev_apps = [os.path.basename(app) for app in Path(DEVELOPMENT_DEPLOY_PATH).iterdir() if os.path.isdir(app)]
    return list(dict.fromkeys(ops_apps + dev_apps))
