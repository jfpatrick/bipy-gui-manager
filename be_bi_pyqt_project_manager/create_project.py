import re
import os
import shutil
from subprocess import Popen, PIPE

from be_bi_pyqt_project_manager import cli_utils as cli


def validate_or_fail(value, validator, feedback):
    """ Either return the value if valid, or throw ValueError """
    if validator(value):
        return value
    raise ValueError(feedback)


def validate_or_ask(validator, question, neg_feedback, start_value="", pos_feedback=None, hints=()):
    """ Either return start_value if valid, or ask the user until they give a valid value """
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
    """
        If an initial value is given and valid, return it.
        If an initial value is given and invalid, fail.
        If it's not given, ask the user until a valid value is received.
    """
    if cli_value and cli_value != "":
        result = validate_or_fail(cli_value, validator, neg_feedback)
        if pos_feedback:
            cli.positive_feedback(pos_feedback.format(result))
        return result
    else:
        return validate_or_ask(validator, question, neg_feedback, pos_feedback=pos_feedback, hints=hints)


def validate_demo_flags(force_demo: bool, demo: bool) -> bool:
    """
    Checks which combination of values are contained in the parameters and returns the correct value
    for parameters.demo, eventually asking the user if necessary
    :param force_demo: whether the --with-demo flag was passed
    :param demo: opposite of whether the --no-demo flag was passed
    :return: True if demo should be included, False otherwise
    """
    if force_demo and demo:
        # --with-demo was passed
        cli.positive_feedback("Your project will contain a demo application.")
        return True
    elif not force_demo and not demo:
        # only --no-demo was passed
        cli.positive_feedback("Your project will not contain the demo application.")
        return False
    elif not force_demo and demo:
        # Neither --with-demo nor --no-demo were passed
        value = cli.ask_input("Do you want to install a demo application within your project? (yes/no)")
        while True:
            if value == "n" or value == "no":
                cli.positive_feedback("Your project will not contain the demo application.")
                return False
            elif value == "y" or value == "yes":
                cli.positive_feedback("Your project will contain a demo application.")
                return True
            else:
                value = cli.handle_failure("Please type yes or no:")


def invoke_git(parameters=(), cwd=os.getcwd(), allow_retry=False, neg_feedback="An error occurred in Git!"):
    """
    Perform a syscall to the local Git executable
    :param parameters: parameters to pass to Git, as an array
    :param cwd: working directory for Git
    :param allow_retry: on fail, let the user decide if they want to retry or not
    :param neg_feedback: message to explain a potential failure
    :return: Nothing if the command succeeds, OSError if it fails
    """
    command = ['/usr/bin/git']
    command.extend(parameters)

    while True:
        git_query = Popen(command, cwd=cwd, stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = git_query.communicate()

        if git_query.poll() == 0:
            return
        else:
            cli.negative_feedback(stderr.decode('utf-8'))

            if not allow_retry:
                raise OSError(neg_feedback)

            answer = cli.handle_failure("Do you want to retry? (yes/no)")
            if answer == "no" or answer == "n":
                raise OSError(neg_feedback)


def create_project(parameters):

    cli.draw_line()
    print("\n  Welcome to BI's PyQt5 Project Setup Wizard!")
    cli.draw_line()
    print("\n  Setup:\n")

    project_name_validator = re.compile("^[a-z0-9-]+$")
    author_email_validator = re.compile("[a-zA-Z0-9._%+-]+@cern.ch")  # TODO support email lists!
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

    gitlab_repo = None
    if parameters.gitlab:
        gitlab_repo = validate_as_arg_or_ask(
            cli_value=parameters.gitlab_repo,
            validator=lambda v: (v == "no-gitlab" or
                                 repo_validator_https.match(v) or
                                 repo_validator_ssh.match(v) or
                                 repo_validator_kerb.match(v)),
            question="Please create a new project on GitLab and paste here the \033[0;32m repository URL\033[0;m "
                     "(or type 'no-gitlab' to skip this step):",
            neg_feedback="Invalid GitLab repository URL.",
            pos_feedback="The project GitLab repository address is set to: {}",
            hints=("copy the address from the Clone button, choosing the protocol you prefer (HTTPS, SSH, KRB5)", )
        )
        if gitlab_repo == 'no-gitlab':
            gitlab_repo = None
            parameters.gitlab = False

    parameters.demo = validate_demo_flags(parameters.force_demo, parameters.demo)

    cli.draw_line()
    print("\n  Installation:\n")
    project_path = os.path.join(os.getcwd(), project_name)

    try:
        cli.positive_feedback("Checking target path")
        check_path_is_available(project_path)

        if parameters.template_path:
            cli.positive_feedback("Copying the template from {}".format(parameters.template_path))
            copy_folder_from_path(parameters.template_path, project_path)
        else:
            cli.positive_feedback("Downloading the template from GitLab")
            download_template(project_path, parameters.clone_protocol, parameters.demo)

        cli.positive_feedback("Applying customizations")
        apply_customizations(project_path, project_name, project_desc, project_author, author_email)

        cli.positive_feedback("Preparing README")
        generate_readme(project_path, project_name, project_desc, project_author, author_email)
        cli.give_hint("check the README for typos and complete it with a more in-depth description of your project.")

        cli.positive_feedback("Setting up local Git repository")
        init_local_repo(project_path)

        if parameters.gitlab:
            cli.positive_feedback("Uploading project on GitLab")
            push_first_commit(project_path, gitlab_repo)

        cli.positive_feedback("Installing the project in a new virtualenv")
        install_project(project_path)

        cli.draw_line()
        print("")
        cli.positive_feedback("New project '{}' installed successfully".format(project_name))
        cli.positive_feedback(
            "Please make sure by typing 'source activate.sh' and '{}' in the console".format(project_name))
        cli.give_hint("type 'pyqt-manager --help' to see more workflows.")
        cli.give_hint("launch PyCharm from the project folder to start working - "
                      "remember to type 'source activate.sh' in PyCharm terminal too")
        cli.draw_line()

    except Exception as e:
        cli.negative_feedback("A fatal error occurred: {}".format(e))
        cli.negative_feedback("Exiting")
        cli.draw_line()


def check_path_is_available(project_path: str) -> None:
    """
    Makes sure there is no folder with the name of the new project and if so ask the user and act accordingly.
    :param project_path: path to the new project
    """
    if os.path.exists(project_path):
        answer = cli.handle_failure("A folder called '{}' already exists. ".format(project_path) +
                                    "Do you want to overwrite it? (yes/no)")
        if answer == "yes" or answer == "y":
            shutil.rmtree(project_path)
        elif answer == "no" or answer == "n":
            raise OSError("Directory '{}' already exists.".format(project_path))


def copy_folder_from_path(source_path: str, dest_path: str) -> None:
    """
    Copy the content of a folder into a newly created target folder
    :param source_path: path to copy the content of
    :param dest_path: folder to be created with the specified content
    """
    shutil.copytree(source_path, dest_path)
    shutil.move(source_path, os.path.join(os.path.dirname(source_path), os.path.basename(dest_path)))


def download_template(project_path: str, clone_protocol: str, get_demo: bool) -> None:
    """
    Downloads the template code from its GitLab repository
    :param project_path: Where to clone the template (folder must not exists)
    :param clone_protocol: use HTTPS, SSH or Kerberos
    :param get_demo: Clone the template with the demo application or without.
    """
    if clone_protocol == 'https':
        template_url = 'https://gitlab.cern.ch/szanzott/be-bi-pyqt-template.git'
    elif clone_protocol == 'kerberos':
        template_url = 'https://:@gitlab.cern.ch:8443/szanzott/be-bi-pyqt-template.git'
    elif clone_protocol == 'ssh':
        template_url = 'ssh://git@gitlab.cern.ch:7999/szanzott/be-bi-pyqt-template.git'
    else:
        raise ValueError("Clone protocol not recognized: {}".format(clone_protocol))

    if get_demo:
        git_command = ['clone', template_url, project_path]
    else:
        git_command = ['clone', '--single-branch', '--branch', 'no-demo', template_url,
                       project_path]
    invoke_git(
        parameters=git_command,
        cwd=os.getcwd(),
        allow_retry=True,
        neg_feedback="Failed to clone the template!"
    )


def apply_customizations(project_path: str, project_name: str, project_desc: str, project_author: str,
                         project_email: str) -> None:
    """
    Modify the template by applying all the customizations specified in setup.
    :param project_path: path to the project folder
    :param project_name: name of the project
    :param project_desc: description of the project
    :param project_author: name of the project's author
    :param project_email: email of the project's author, or support email
    """
    project_name_underscores = project_name.replace("-", "_")
    project_name_capitals = project_name.replace("-", " ").title()
    try:
        # Rename the root dir and remove the image folder
        shutil.move("{}/be_bi_pyqt_template".format(project_path),
                    "{}/{}".format(project_path, project_name_underscores))
        shutil.rmtree("{}/images".format(project_path))
        # Edit the files and double-check on the directories
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

    except Exception as e:
        cli.negative_feedback("Failed to apply customizations")
        raise e


def generate_readme(project_path: str, project_name: str, project_desc: str, project_author: str,
                    project_email: str) -> None:
    """
    Generate a README with the invariant informations, like how to install, run tests, debug, etc...
    :param project_path: path to the project folder
    :param project_name: name of the project
    :param project_desc: description of the project
    :param project_author: name of the project's author
    :param project_email: email of the project's author, or support email
    """
    project_name_capitals = project_name.replace("-", " ").title()
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

    except Exception as e:
        cli.negative_feedback("Failed to generate README")
        raise e


def init_local_repo(project_path: str) -> None:
    """
    Initialize the project's git repo.
    :param project_path: Path to the project root
    """
    shutil.rmtree("{}/.git".format(project_path))
    invoke_git(
        parameters=['init'],
        cwd=project_path,
        allow_retry=False,
        neg_feedback="Failed to init the repo in the project folder."
    )
    invoke_git(
        parameters=['add', '--all'],
        cwd=project_path,
        allow_retry=False,
        neg_feedback="Failed to stage the template."
    )
    invoke_git(
        parameters=['commit', '-m', 'Initial commit ' +
                    '(from pyqt-manager https://gitlab.cern.ch/szanzott/be-bi-pyqt-project-manager )'],
        cwd=project_path,
        allow_retry=False,
        neg_feedback="Failed to commit the template."
    )


def push_first_commit(project_path: str, gitlab_repo: str) -> None:
    """
    Adds a remote to the Git repo and pushes the first commit
    :param project_path: Path to the project root
    :param gitlab_repo: GitLab repo to push to
    """
    invoke_git(
        parameters=['remote', 'add', 'origin', gitlab_repo],
        cwd=project_path,
        allow_retry=False,
        neg_feedback="Failed to add the remote on the project's local repo."
    )
    invoke_git(
        parameters=['push', '-u', 'origin', 'master'],
        cwd=project_path,
        allow_retry=False,
        neg_feedback="Failed to push the first commit to GitLab."
    )


def install_project(project_path: str) -> None:
    """
    Copies a bash script into the project, executes it and remove it.
    The bash script will activate the venvs and install the project in its own
    virtual environment.
    :param project_path: Path to the project root
    """
    # Copy shell script in project
    script_temp_location = os.path.join(project_path, ".tmp.sh")
    shutil.copy(os.path.join(os.path.dirname(__file__), "install-project.sh"), script_temp_location)
    # Execute it (create venvs and install folder in venv)\
    os.chmod(script_temp_location, 0o777)
    # os.system("chmod +x {}".format(script_temp_location))
    error = os.WEXITSTATUS(os.system("cd {} && source {}".format(project_path, script_temp_location)))
    # Remove temporary script
    os.remove(script_temp_location)
    if error:
        cli.negative_feedback("New project failed to install: {}.".format(error))
        cli.negative_feedback("Please execute 'source activate.sh' and 'pip install -e .'"
                              "in the project's root and, if it fails, send the log to the maintainers.")
        raise OSError("New project failed to install: {}.".format(error))



