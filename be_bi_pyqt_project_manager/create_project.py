import re
import os
import shutil
from pathlib import Path
from subprocess import Popen, PIPE

from be_bi_pyqt_project_manager import cli_utils as cli


def create_project(parameters):

    cli.draw_line()
    print("\n  Welcome to BI's PyQt5 Project Setup Wizard!")
    cli.draw_line()
    print("  Setup:\n")

    project_name: str = None
    project_desc: str = None
    project_author: str = None
    author_email: str = None
    project_name_validator = re.compile("^[a-z0-9\-]+$")
    author_email_validator = re.compile("[a-zA-Z0-9._%+-]+@cern\.ch")

    while not project_name:
        project_name = cli.ask_input("Please enter your \033[0;32mproject's name\033[0;m:")
        if not project_name_validator.match(project_name):
            project_name = None
            cli.negative_feedback("The project name can contain only letters, numbers and dashes.")

    while not project_desc:
        project_desc = cli.ask_input("Please enter a \033[0;32mone-line description\033[0;m of your project:")
        if "\"" in project_desc:
            project_desc = None
            cli.negative_feedback("The project description cannot contain the character \".")

    while not project_author:
        project_author = cli.ask_input("Please enter the project's \033[0;32mauthor name\033[0;m:")
        if "\"" in project_author:
            project_author = None
            cli.negative_feedback("The name cannot contain the character \".")

    while not author_email:
        author_email = cli.ask_input("Please enter the author's \033[0;32mCERN email address\033[0;m:")
        if not author_email_validator.match(author_email):
            author_email = None
            cli.negative_feedback("Invalid CERN email, try again")

    cli.draw_line()
    print("\n  Installation:\n")

    cli.positive_feedback("Downloading template from GitLab...")
    if not download_template(project_name): return
    cli.success_feedback()

    cli.positive_feedback("Creating project under {}/...".format(project_name))
    if not create_directories(project_name): return
    cli.success_feedback()

    cli.positive_feedback("Applying customizations...")
    # Do it
    cli.success_feedback()

    cli.positive_feedback("Preparing README...")

    cli.give_hint("check the README for typos, as it was auto-generated")
    # Do it
    cli.success_feedback()

    cli.positive_feedback("Activating virtualenvs...")
    # Do it
    cli.success_feedback()

    cli.positive_feedback("Installing the project...")
    # Do it
    cli.success_feedback()

    cli.positive_feedback("Preparing README...")
    # Do it
    cli.success_feedback()


def download_template(project_name):
    success = False
    while not success:
        # global_config = git.GitConfigParser([os.path.normpath(os.path.expanduser("~/.gitconfig"))], read_only=True)
        # global_config.set_value("core", "askPass", "").release()
        try:
            git_command = ['/usr/bin/git', 'clone', 'https://gitlab.cern.ch/szanzott/be-bi-pyqt-template.git',
                           project_name]
            git_query = Popen(git_command, cwd=os.getcwd(), stdout=PIPE, stderr=PIPE)
            (git_status, error) = git_query.communicate()

            if git_query.poll() == 0:
                success = True
            else:
                answer = cli.handle_failure("Failed to clone the template! Do you want to retry? (yes/no)")
                if answer == "no" or answer == "n":
                    # Terminate here
                    return False

        except Exception:
            cli.negative_feedback("Failed to invoke git. Please make sure git is installed and retry.")
            return False
    return True


def create_directories(project_name):
    project_name_underscores = project_name.replace("-", "_")
    success = False
    while not success:
        try:
            shutil.move("{}/be_bi_pyqt_template".format(project_name), "{}/{}".format(project_name, project_name_underscores))
            shutil.rmtree("{}/images".format(project_name))
            success = True
        except Exception as e:
            cli.negative_feedback("Failed to refactor the template! Exiting.")
            print(e)
            return False
    return True