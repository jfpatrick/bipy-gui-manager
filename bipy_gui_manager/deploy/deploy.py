import os
import logging
import argparse
from pathlib import Path

from bipy_gui_manager import OPERATIONAL_DEPLOY_PATH, DEVELOPMENT_DEPLOY_PATH, ACC_PY_PATH
from bipy_gui_manager.utils import cli as cli
from bipy_gui_manager.utils import version_control as vcs

APP_DEPLOY_SCRIPT = (Path(__file__).parent / "resources" / "app_deploy.sh").absolute()


def deploy(parameters: argparse.Namespace):
    """
    Script for the 'BI local deploy' procedure. All it does is to call a small Bash script that
    installs the given project in a shared folder, where the AppLauncher can find it.
    :param parameters: the parameters passed through the CLI, if any
    :return: None, but deploys the GUI on a BI-owned shared folder.
    """
    if parameters.verbose:
        logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.DEBUG)

    if not parameters.path:
        raise ValueError("Path was not specified as a CLI argument and the default (os.getcwd()) was not applied. "
                         "Please debug.")
    path = Path(parameters.path).absolute()
    repo_path = OPERATIONAL_DEPLOY_PATH if parameters.operational else DEVELOPMENT_DEPLOY_PATH

    try:
        # Ensures the current project is a releasable project
        if not vcs.is_git_folder(path) or not is_python_project(path):
            cli.negative_feedback("You are not in a project that can be deployed. Please cd into your expert GUIs "
                                  "folder and run this command again.")
            cli.give_hint("this command checks for the presence of a Git repository and verifies that it "
                          "contains either:"
                          "\n             - a setup.py"
                          "\n             - a folder called 'app' containing your ComRAD app and a 'pyproject.toml'."
                          "\n            Use `bipy-gui-manager -v deploy [ARGS]` to enable debug messages if needed.")
            return

        cli.positive_feedback(f"Running checks on {os.path.basename(path)}...", newline=False)

        if not is_ready_to_deploy(path):
            # The method itself provides feedback on failure already
            return

        if not parameters.project_type:
            parameters.project_type = find_project_type(path)

        cli.positive_feedback("The project is ready to deploy")
        cli.positive_feedback(f"Deploying {os.path.basename(path)}..", newline=False)

        verbose = "1" if parameters.verbose else "0"
        bash = f"/bin/bash -c \"{APP_DEPLOY_SCRIPT} {path} {repo_path} {ACC_PY_PATH} {parameters.project_type} " \
               f"{verbose}\""
        logging.debug(f"Executing app_deploy.sh: {bash}")
        error = os.WEXITSTATUS(os.system(bash))
        if error:
            cli.negative_feedback(f"Deploy failed: {error}")
            cli.give_hint("To be able to deploy, you must be in your virtualenv! Type 'source activate.sh' in the "
                          "root of your project if you haven't done so already. If you see errors, do it again on a "
                          "new terminal window.")
            logging.debug("Deploy failed.")
            return

        cli.positive_feedback(f"New project {os.path.basename(path)} deployed successfully. "
                              "It should now be available to the AppLauncher.")
    except OSError as e:
        logging.debug(e)
        cli.negative_feedback("Exiting")
        return


def is_python_project(path_to_check: str):
    """
    :param path_to_check: path that should contain the Python project.
    :return: True if the path contains a setup.py or a pyproject.toml in the expected location, False otherwise
    """
    if os.path.isdir(path_to_check):
        if os.path.exists(os.path.join(path_to_check, "setup.py")) and \
                os.path.exists(os.path.join(path_to_check, "app/pyproject.toml")):
            cli.negative_feedback("Your application contains both a setup.py and a pyproject.toml file! "
                                  "The setup.py is going to be ignored and the application is going to be "
                                  "deployed as a ComRAD app.")
            return True
        if os.path.exists(os.path.join(path_to_check, "setup.py")):
            logging.debug(f"{path_to_check} is a PyQt application.")
            return True
        if os.path.exists(os.path.join(path_to_check, "app/pyproject.toml")):
            logging.debug(f"{path_to_check} is a ComRAD application.")
            return True
    logging.debug(f"Neither setup.py nor app/pyproject.toml were found under {path_to_check}")
    return False


def find_project_type(path_to_check: str):
    """
    :param path_to_check: path that should contain the Python project.
    :return: 'pyqt' if the path contains a setup.py, 'comrad' if it contains a pyproject.toml under the folder app/.
    :raises ValueError if the folder does not exist or contains neither file.
    """
    if not os.path.isdir(path_to_check):
        raise ValueError(f"The folder '{path_to_check}' does not exist")

    if not is_python_project(path_to_check):
        raise ValueError(f"Cannot identify the project type: '{path_to_check}' contains neither a setup.py "
                         "nor a app/pyproject.toml")

    if os.path.exists(os.path.join(path_to_check, "app/pyproject.toml")):
        return 'comrad'

    if os.path.exists(os.path.join(path_to_check, "setup.py")):
        return 'pyqt'


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
        return False
    return True
