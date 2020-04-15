import re
import os
import shutil
from subprocess import Popen, PIPE

from be_bi_pyqt_project_manager import cli_utils as cli


def validate_and_fail(value, validator, feedback):
    if validator(value):
        return value
    raise ValueError(feedback)


def validate_and_ask(validator, question, neg_feedback, start_value="", pos_feedback=None, hints=()):
    value = start_value
    while not validator(value):
        if value != "":
            cli.negative_feedback(neg_feedback)
            for hint in hints:
                cli.give_hint(hint)
        value = cli.ask_input(question)
    if pos_feedback:
        cli.positive_feedback(pos_feedback.format(value))
    return value


def validate_as_arg_or_ask(cli_value, validator, question, neg_feedback, pos_feedback=None, hints=()):
    if cli_value and cli_value != "":
        result = validate_and_fail(cli_value, validator, neg_feedback)
        if pos_feedback:
            cli.positive_feedback(pos_feedback.format(result))
        return result
    else:
        return validate_and_ask(validator, question, neg_feedback, pos_feedback=pos_feedback, hints=hints)


def create_project(parameters):

    cli.draw_line()
    print("\n  Welcome to BI's PyQt5 Project Setup Wizard!")
    cli.draw_line()
    print("\n  Setup:\n")

    project_name_validator = re.compile("^[a-z0-9-]+$")
    author_email_validator = re.compile("[a-zA-Z0-9._%+-]+@cern.ch")
    repo_validator_ssh = re.compile("^ssh://git@gitlab.cern.ch:7999/[a-zA-Z0-9_%-]+/[a-zA-Z0-9_%/-]+.git$")
    repo_validator_https = re.compile("^https://gitlab.cern.ch/[a-zA-Z0-9_%-]+/[a-zA-Z0-9_%/-]+.git$")
    repo_validator_kerb = re.compile("^https://:@gitlab.cern.ch:8443/[a-zA-Z0-9_%-]+/[a-zA-Z0-9_%/-]+.git$")

    project_name = validate_as_arg_or_ask(
        cli_value=parameters.project_name,
        validator=lambda v: project_name_validator.match(v),
        question="Please enter your \033[0;32mproject's name\033[0;m:",
        neg_feedback="The project name can contain only lowercase letters, numbers and dashes.",
        pos_feedback="The project name is set to: {}"
    )
    project_desc = validate_as_arg_or_ask(
        cli_value=parameters.project_desc,
        validator=lambda v: v != "" and "\"" not in v,
        question="Please enter a \033[0;32mone-line description\033[0;m of your project:",
        neg_feedback="The project description cannot contain the character \".",
        pos_feedback="The project description is set to: {}"
    )
    project_author = validate_as_arg_or_ask(
        cli_value=parameters.project_author,
        validator=lambda v: v != "" and "\"" not in v,
        question="Please enter the project's \033[0;32mauthor name\033[0;m:",
        neg_feedback="The author name cannot contain the character \".",
        pos_feedback="The project author name is set to: {}"
    )
    author_email = validate_as_arg_or_ask(
        cli_value=parameters.author_email,
        validator=lambda v: author_email_validator.match(v),
        question="Please enter the author's \033[0;32mCERN email address\033[0;m:",
        neg_feedback="Invalid CERN email.",
        pos_feedback="The project author's email name is set to: {}"
    )
    if parameters.gitlab:
        gitlab_repo = validate_as_arg_or_ask(
            cli_value=parameters.gitlab_repo,
            validator=lambda v: (repo_validator_https.match(v) or
                                 repo_validator_ssh.match(v) or
                                 repo_validator_kerb.match(v)),
            question="Please create a new project on GitLab and past here the \033[0;32m repository URL\033[0;m:",
            neg_feedback="Invalid GitLab repository URL.",
            pos_feedback="The project GitLab repository address is set to: {}",
            hints=("copy the address from the Clone button, choosing the protocol you prefer (HTTPS, SSH, KRB5)", )
        )

    cli.draw_line()
    print("\n  Installation:\n")
    project_path = os.path.join(os.getcwd(), project_name)

    cli.positive_feedback("Preparing to get template code...")
    if not download_template(project_path, parameters.clone_protocol, parameters.template_path, parameters.demo):
        return

    cli.positive_feedback("Creating project under {}/...".format(project_name))
    if not create_directories(project_path, project_name):
        return

    cli.positive_feedback("Applying customizations...")
    if not apply_customizations(project_path, project_name, project_desc, project_author, author_email):
        return

    cli.positive_feedback("Preparing README...")
    if not generate_readme(project_path, project_name, project_desc, project_author, author_email):
        return
    cli.give_hint("check the README for typos and complete it with a more in-depth description of your project.")

    if parameters.gitlab:
        cli.positive_feedback("Uploading to GitLab...")
    else:
        cli.positive_feedback("Setting up local Git repository...")
        gitlab_repo = None
    if not push_first_commit(project_path, gitlab_repo, parameters.gitlab):
        return

    cli.positive_feedback("Installing the project in a new virtualenv...")
    if not install_project(project_path, project_name):
        return


def download_template(project_path, clone_protocol, custom_path, get_demo):
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
                return False

        # Copy from custom path
        if custom_path:
            cli.positive_feedback("Copying the template from {} ...".format(custom_path))
            os.system("mkdir {}".format(project_path))
            copy_process = Popen(["cp", "-R", "{}/.".format(custom_path), project_path], stdout=PIPE, stderr=PIPE)
            (stdout, stderr) = copy_process.communicate()

            if copy_process.poll() == 0:
                return True
            else:
                cli.negative_feedback(stderr.decode('utf-8'))
                answer = cli.handle_failure("Failed to copy the template! Do you want to retry? (yes/no)")
                if answer == "no" or answer == "n":
                    cli.give_hint("You can debug this issue by checking the logs of " +
                                  "'cp -r {} {}' ".format(custom_path, project_path) +
                                  "in the current directory.")
                    # Terminate here
                    return False

        # Invoke git
        try:
            cli.positive_feedback("Downloading template from GitLab...")
            if clone_protocol == 'https':
                template_url = 'https://gitlab.cern.ch/szanzott/be-bi-pyqt-template.git'
            elif clone_protocol == 'kerberos':
                template_url = 'https://:@gitlab.cern.ch:8443/szanzott/be-bi-pyqt-template.git'
            elif clone_protocol == 'ssh':
                template_url = 'ssh://git@gitlab.cern.ch:7999/szanzott/be-bi-pyqt-template.git'
            else:
                cli.negative_feedback("Pull protocol not recognized: {}".format(clone_protocol))
                return False

            if get_demo:
                git_command = ['/usr/bin/git', 'clone', template_url, project_path]
            else:
                git_command = ['/usr/bin/git', 'clone', '--single-branch', '--branch', 'no-demo', template_url,
                               project_path]
            git_query = Popen(git_command, cwd=os.getcwd(), stdout=PIPE, stderr=PIPE)
            (stdout, stderr) = git_query.communicate()

            if git_query.poll() == 0:
                success = True
            else:
                cli.negative_feedback(stderr)
                answer = cli.handle_failure("Failed to clone the template! Do you want to retry? (yes/no)")
                if answer == "no" or answer == "n":
                    cli.give_hint("You can debug this issue by checking the logs of " +
                                  "'git clone {}' ".format(template_url) +
                                  "in the current directory.")
                    # Terminate here
                    return False

        except Exception as e:
            cli.negative_feedback("Failed to invoke git. Please make sure git is installed and working and retry.")
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
            cli.negative_feedback("Failed to apply customizations!")
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


def push_first_commit(project_path, gitlab_repo, perform_upload):
    success = False
    while not success:

        # Invoke git
        try:
            os.system("rm -rf {}/.git".format(project_path))
            git_command = ['/usr/bin/git', 'init']
            git_query = Popen(git_command, cwd=project_path, stdout=PIPE, stderr=PIPE)
            (stdout, stderr) = git_query.communicate()

            if git_query.poll() != 0:
                cli.negative_feedback("Failed to init the repo in the project folder!")
                cli.negative_feedback(stderr)
                cli.give_hint("You can debug this issue by checking the logs of 'git init' in the project directory.")
                return False

            if perform_upload:
                git_command = ['/usr/bin/git', 'remote', 'add', 'origin', gitlab_repo]
                git_query = Popen(git_command, cwd=project_path, stdout=PIPE, stderr=PIPE)
                (stdout, stderr) = git_query.communicate()

                if git_query.poll() != 0:
                    cli.negative_feedback("Failed to add the remote on the project's local repo!")
                    cli.negative_feedback(stderr)
                    cli.give_hint("You can debug this issue by checking the logs of "
                                  "'git remote add origin {}' and 'git remote -v' "
                                  "in the project directory.".format(gitlab_repo))
                    return False

            git_command = ['/usr/bin/git', 'add', '--all']
            git_query = Popen(git_command, cwd=project_path, stdout=PIPE, stderr=PIPE)
            (stdout, stderr) = git_query.communicate()

            if git_query.poll() != 0:
                cli.negative_feedback("Failed to stage the template!")
                cli.negative_feedback(stderr)
                cli.give_hint("You can debug this issue by checking the logs of "
                              "'git add --all' in the project directory.".format(gitlab_repo))
                return False

            git_command = ['/usr/bin/git', 'commit', '-m', 'Initial commit ' +
                           '(from pyqt-manager https://gitlab.cern.ch/szanzott/be-bi-pyqt-project-manager )']
            git_query = Popen(git_command, cwd=project_path, stdout=PIPE, stderr=PIPE)
            (stdout, stderr) = git_query.communicate()

            if git_query.poll() != 0:
                cli.negative_feedback("Failed to commit the template!")
                cli.negative_feedback(stderr)
                cli.give_hint("You can debug this issue by checking the logs of "
                              "'git commit -m \"Initial commit\"' in the project directory.".format(gitlab_repo))
                return False

            if perform_upload:
                git_command = ['/usr/bin/git', 'push', '-u', 'origin', 'master']
                git_query = Popen(git_command, cwd=project_path, stdout=PIPE, stderr=PIPE)
                (stdout, stderr) = git_query.communicate()

                if git_query.poll() != 0:
                    cli.negative_feedback("Failed to push the first commit to GitLab!")
                    cli.negative_feedback(stderr)
                    cli.give_hint("You can debug this issue by checking the logs of "
                                  "'git push -u origin master' "
                                  "in the project directory.".format(gitlab_repo))
                    return False
            success = True

        except Exception as e:
            cli.negative_feedback("Failed to setup the repository. "
                                  "Please make sure git is installed and working and retry.")
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
            raise OSError("New project failed to install: {}.".format(error))

        cli.success_feedback()
        cli.draw_line()
        print("")
        cli.positive_feedback("New project '{}' installed successfully".format(project_name))
        cli.positive_feedback("Please make sure by typing 'source activate.sh' and '{}' in the console".format(project_name))
        cli.give_hint("type 'pyqt-manager --help' to see more workflows.")
        cli.give_hint("launch PyCharm from the project folder to start working - "
                      "remember to type 'source activate.sh' in PyCharm terminal too")
        cli.draw_line()

    except Exception as e:
        cli.negative_feedback(e)
        cli.negative_feedback("Please execute 'source activate.sh' and 'pip install -e .'"
                              "in the project's root and, if it fails, send the log to the maintainers.")
        cli.draw_line()
        return False
    return True


