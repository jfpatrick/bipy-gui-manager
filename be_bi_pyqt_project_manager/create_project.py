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
    print("\n  Setup:\n")

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
    project_path = os.path.join(os.getcwd(), project_name)

    cli.positive_feedback("Downloading template from GitLab...")
    if not download_template(project_path): return
    cli.success_feedback()

    cli.positive_feedback("Creating project under {}/...".format(project_name))
    if not create_directories(project_path, project_name): return
    cli.success_feedback()

    cli.positive_feedback("Applying customizations...")
    if not apply_customizations(project_path, project_name, project_desc, project_author, author_email): return
    cli.success_feedback()

    cli.positive_feedback("Preparing README...")
    if not generate_readme(project_path, project_name, project_desc, project_author, author_email): return
    cli.give_hint("check the README for typos, as it was auto-generated")
    cli.success_feedback()

    cli.positive_feedback("Installing the project in a new virtualenv...")
    if not install_project(project_path, project_name): return


def download_template(project_path):
    success = False
    while not success:

        # Check if the folder does not exist already, or git will fail
        if os.path.exists(project_path):
            answer = cli.handle_failure("A folder called '{}' already exists in this folder. ".format(project_path) +
                                        "Do you want to overwrite it? (yes/no)")
            if answer == "yes" or answer == "y":
                shutil.rmtree(project_path)
            else:
                cli.negative_feedback("Directory '{}' already exists. Exiting.".format(project_path))

        # Invoke git
        try:
            git_command = ['/usr/bin/git', 'clone', 'https://gitlab.cern.ch/szanzott/be-bi-pyqt-template.git',
                           project_path]
            git_query = Popen(git_command, cwd=os.getcwd(), stdout=PIPE, stderr=PIPE)
            (stdout, stderr) = git_query.communicate()

            if git_query.poll() == 0:
                success = True
            else:
                cli.negative_feedback(stderr)
                answer = cli.handle_failure("Failed to clone the template! Do you want to retry? (yes/no)")
                if answer == "no" or answer == "n":
                    cli.give_hint("You can debug this issue by checking the logs of "
                                  "'git clone https://gitlab.cern.ch/szanzott/be-bi-pyqt-template.git' "
                                  "in the current directory.")
                    # Terminate here
                    return False

        except Exception as e:
            cli.negative_feedback("Failed to invoke git. Please make sure git is installed and retry.")
            print(e)
            return False
    return True


def create_directories(project_path, project_name):
    project_name_underscores = project_name.replace("-", "_")
    success = False
    while not success:
        try:
            shutil.move("{}/be_bi_pyqt_template".format(project_path), "{}/{}".format(project_path, project_name_underscores))
            shutil.rmtree("{}/images".format(project_path))
            os.remove("{}/setup.sh".format(project_path))
            success = True
        except Exception as e:
            cli.negative_feedback("Failed to refactor the template! Exiting.")
            print(e)
            return False
    return True


def apply_customizations(project_path, project_name, project_desc, project_author, project_email):
    project_name_underscores = project_name.replace("-", "_")
    project_name_capitals = project_name.replace("-", " ").title()
    success = False
    while not success:
        try:
            for rootdir, dirs, files in os.walk(project_path):
                for filename in files:
                    filepath = os.path.join(rootdir, filename)
                    # Filtering to avoid binary files
                    if filename.split(".")[-1] in ["py", "md", "ui", "qrc", "yml", "gitignore", "sh"]:
                        with open(filepath, 'r') as f:
                            s = f.read()
                        s = s.replace("be-bi-pyqt-template", project_name)
                        s = s.replace("be_bi_pyqt_template", project_name_underscores)
                        s = s.replace("BE BI PyQt Template Code", project_desc)
                        s = s.replace("BE BI PyQt Template", project_name_capitals)
                        s = s.replace("Sara Zanzottera", project_author)
                        s = s.replace("sara.zanzottera@cern.ch", project_email)
                        with open(filepath, "w") as f:
                            f.write(s)
                for dirname in dirs:
                    if "be_bi_pyqt_template" in dirname:
                        dirpath = os.path.join(rootdir, dirname)
                        os.rename(dirpath, dirpath.replace("be_bi_pyqt_template", project_name_underscores))
                    if "be-bi-pyqt-template" in dirname:
                        dirpath = os.path.join(rootdir, dirname)
                        os.rename(dirpath, dirpath.replace("be-bi-pyqt-template", project_name))
            success = True
        except Exception as e:
            cli.negative_feedback("Failed to apply customizations! Exiting.")
            print(e)
            return False
    return True


def generate_readme(project_path, project_name, project_desc, project_author, project_email):
    project_name_capitals = project_name.replace("-", " ").title()
    success = False
    while not success:
        try:
            os.remove(os.path.join(project_path, "README.md"))
            os.rename(os.path.join(project_path, "README-template.md"), os.path.join(project_path, "README.md"))
            readme = os.path.join(project_path, "README.md")
            with open(readme) as f:
                s = f.read()
            s = s.replace("project-name", project_name)
            s = s.replace("Project Name", project_name_capitals)
            s = s.replace("_Here goes the project description_", project_desc)
            s = s.replace("the project author", project_author)
            s = s.replace("author@cern.ch", project_email)
            with open(readme, "w") as f:
                f.write(s)
            success = True
        except Exception as e:
            cli.negative_feedback("Failed to generate README! Exiting.")
            print(e)
            return False
    return True


def install_project(project_path, project_name):
    try:
        # Copy shell script in project
        script_temp_location = os.path.join(project_path, ".tmp.sh")
        shutil.copy(os.path.join(os.path.dirname(__file__), "install-project.sh"), script_temp_location)
        # Execute it (create venvs and install folder in venv)
        os.system("chmod +x {}".format(script_temp_location))
        error = os.WEXITSTATUS(os.system("cd {} && source {}".format(project_path, script_temp_location)))
        # Remove temporary script
        os.remove(script_temp_location)
        if error:
            raise OSError("New project failed to install.")

        cli.success_feedback()
        cli.draw_line()
        cli.positive_feedback("New project '{}' installed successfully!".format(project_name))
        cli.positive_feedback("Please make sure by typing 'source activate.sh' and '{}' in the console".format(project_name))
        cli.give_hint("type 'pyqt-manager --help' to see more workflows.")
        cli.draw_line()

    except Exception as e:
        cli.negative_feedback(e)
        cli.negative_feedback("Please execute 'source activate.sh' and 'pip install -e .'"
                              "in the project's root and, if it fails, send the log to the maintainers.")
        cli.draw_line()
        return False
    return True


