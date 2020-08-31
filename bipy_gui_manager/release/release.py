import os
import sys
import shutil
import logging
import argparse
import pkg_resources
from pathlib import Path

from bipy_gui_manager.utils import cli as cli
from bipy_gui_manager.utils import version_control as vcs

DEPLOY_FOLDER = "/user/bdisoft/development/python/gui/deployments" # "/afs/cern.ch/work/s/szanzott/public/GUI/deploy-folder"
DEPLOY_FOLDER_DEBUG = Path(__file__).parent.parent.parent / "deploy-folder-debug"


def release(parameters: argparse.Namespace):
    """
    Script for the 'BI local release' procedure. All it does is to call a small Bash script that
    installs the given project in a shared folder, where the AppLauncher can find it.
    :param parameters: the parameters passed through the CLI, if any
    :return: None, but deploys the GUI on a BI-owned shared folder.
    """
    if parameters.verbose or parameters.debug:
        logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.DEBUG)

    deploy_folder: Path
    if parameters.debug:
        os.makedirs(DEPLOY_FOLDER_DEBUG, exist_ok=True)
        deploy_folder = Path(DEPLOY_FOLDER_DEBUG)
    else:
        deploy_folder = Path(DEPLOY_FOLDER)

    if not parameters.path:
        raise ValueError("Path was not specified as a CLI argument and the default (os.getcwd()) was not applied. "
                         "Please debug.")
    path = Path(parameters.path).absolute()

    try:
        # Ensures the current project is a releasable project
        if not vcs.is_git_folder(path) or not is_python_project(path):
            cli.negative_feedback("You are not in a project that can be released. Please cd into your expert GUIs "
                                  "folder and run this command again.")
            cli.give_hint("NOTE: this command checks for the presence of a Git repository and verifies that it "
                          "contains a Python project. Use `bipy-gui-manager -v release` to enable debug messages if "
                          "necessary.")
            return

        cli.positive_feedback(f"Running checks on {os.path.basename(path)}...", newline=False)

        if not is_ready_to_deploy(path):
            # The method itself provides feedback on failure already
            return
        cli.positive_feedback("The project is ready to deploy")
        cli.positive_feedback(f"Deploying {os.path.basename(path)}..", newline=False)

        # Find the entry point
        # if parameters.entry_point:
        #     entry_point = parameters.entry_point
        # else:
        #     entry_point = os.path.basename(path)
        # repo_url = vcs.get_remote_url(path)
        #
        # # Get the remote for the current directory
        # logging.debug("Getting remote URL...")
        # remote_url = vcs.get_remote_url(path)
        # logging.debug(f"The remote URL is {remote_url}")

        # logging.debug(f"Saving current directory: {os.getcwd()}")
        # current_dir = os.getcwd()
        # logging.debug(f"Moving to the shared GUI deploy folder: {deploy_folder}")
        # os.chdir(str(deploy_folder))
        # logging.debug("Copying appinstaller.sh into target folder")
        # shutil.copy(str(Path(__file__).parent / 'resources' / 'appinstaller.sh'), str(deploy_folder))
        logging.debug("Executing appinstaller.sh")
        #error = os.WEXITSTATUS(os.system(f"/bin/bash -c \"./appinstaller.sh {entry_point} {repo_url}\""))
        appinstaller = (Path(__file__).parent / "resources" / "appinstaller.sh").absolute()
        error = os.WEXITSTATUS(os.system(f"/bin/bash -c \"{appinstaller} {path}\""))
        if error:
            cli.negative_feedback("Deploy failed: {}.".format(error))
            logging.debug("Deploy failed.")
            #os.chdir(current_dir)
            return

        # Remove appinstaller.sh
        # os.remove('appinstaller.sh')
        # logging.debug("Deploy successful. Move back to original working directory: {}".format(current_dir))
        # os.chdir(current_dir)

        cli.positive_feedback(f"New project {os.path.basename(path)} deployed successfully. "
                              "It should now be available to the AppLauncher.")
    except OSError as e:
        logging.debug(e)
        cli.negative_feedback("Exiting")
        return


def is_python_project(path_to_check: str):
    """
    Returns True if the path is a releasable Python project, i.e. has a setup.py with an entry point.
    :param path_to_check: path that should contain the Python project.
    :return: True if the path contains a setup.py with an entry point (in the directory itself, not
        in a subdir), False otherwise
    """
    if not os.path.exists(path_to_check) or not os.path.exists(os.path.join(path_to_check, "setup.py")):
        return False
    return True


def is_ready_to_deploy(path_to_check: str):
    """
    Make sure that the folder is on master, everything is committed to GitLab and the working directory is clean.
    :param path_to_check: path to the directory to deploy
    :return: True if all the checks pass, False otherwise
    """
    branch = vcs.get_git_branch(path_to_check)
    logging.debug(f"Current branch: {branch}")
    if branch != 'master':
        cli.negative_feedback("You are currently not on master. Please switch to master with `git checkout master` "
                              "and retry.")
        return False

    if not vcs.is_git_dir_clean(path_to_check):
        cli.negative_feedback("You have uncommitted and/or unpushed changes in your local directory. "
                              "Please commit and push them, then run this command again. "
                              "Type `git status` to see the changes.")
        return False

    if not vcs.get_remote_url(path_to_check):
        cli.negative_feedback("This project seems to be not connected to a GitLab repository. Please setup a remote "
                              "for this repository and then run this command again.")
        cli.give_hint("You can link this folder to a GitLab repo in this way:\n"
                      "         - Create a new repository on GitLab (on your personal space or bisw-python)\n"
                      "         - Click on the Clone button and copy one of the links\n"
                      "         - In this terminal, execute `git remote add -f origin <the URL you copied>`\n"
                      "         - Execute `git push`.\n")
        #return False
    return True
