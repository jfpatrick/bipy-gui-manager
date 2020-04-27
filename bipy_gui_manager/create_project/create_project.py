from typing import Tuple
import re
import os
import json
import argparse
import shutil
try:
    import requests  # requests might not be installed, but is needed only for the avatar upload
except ImportError:
    pass
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from bipy_gui_manager import cli_utils as cli
from bipy_gui_manager.create_project import utils


def create_project(parameters: argparse.Namespace):
    """
    Main 'script' for the creation process. Calls, in order, all the functions required to setup a project properly.
    :param parameters: the parameters passed through the CLI
    :return: None, but creates a project according to the information gathered.
    """
    # Initially defined here to be available for an eventual cleanup procedure, if something goes wrong
    project_path = None
    try:
        cli.print_welcome()
        print("  Setup: \n")

        parameters = gather_setup_information(parameters)
        project_path = os.path.join(parameters.base_path, parameters.project_name)

        group_name = "szanzott"  # "bisw-python"
        create_repo = parameters.gitlab_repo == 'default'
        if parameters.gitlab and parameters.gitlab_repo == 'default':
            if parameters.upload_protocol is None:
                parameters.upload_protocol = parameters.clone_protocol
            if parameters.upload_protocol == 'ssh':
                parameters.gitlab_repo = "ssh://git@gitlab.cern.ch:7999/{}/{}.git".format(group_name,
                                                                                          parameters.project_name)
            elif parameters.upload_protocol == 'https':
                parameters.gitlab_repo = "https://gitlab.cern.ch/{}/{}.git".format(group_name,
                                                                                   parameters.project_name)
            elif parameters.upload_protocol == 'kerberos':
                parameters.gitlab_repo = "https://:@gitlab.cern.ch:8443/{}/{}.git".format(group_name,
                                                                                          parameters.project_name)
            else:
                raise ValueError("Upload protocol not recognized: '{}'".format(parameters.upload_protocol))

        cli.draw_line()
        print("  Installation:\n")

        cli.positive_feedback("Checking target path")
        check_path_is_available(project_path, parameters.interactive, parameters.overwrite)

        if parameters.template_path:
            cli.positive_feedback("Copying the template from {}".format(parameters.template_path))
            copy_folder_from_path(parameters.template_path, project_path)
        else:
            cli.positive_feedback("Downloading the template from GitLab")
            download_template(project_path, parameters.clone_protocol, parameters.demo, parameters.interactive)

        cli.positive_feedback("Applying customizations")
        apply_customizations(project_path, parameters.project_name, parameters.project_desc, parameters.project_author,
                             parameters.author_email)

        cli.positive_feedback("Preparing README")
        generate_readme(project_path, parameters.project_name, parameters.project_desc, parameters.project_author,
                        parameters.author_email, parameters.gitlab_repo)
        cli.give_hint("check the README for typos and complete it with a more in-depth description of your project.")

        cli.positive_feedback("Setting up local Git repository")
        init_local_repo(project_path)

        if parameters.gitlab and create_repo:
            cli.positive_feedback("Creating repository on GitLab")
            create_gitlab_repository(parameters.project_name, parameters.project_desc)

        if parameters.gitlab:
            cli.positive_feedback("Uploading project on GitLab")
            push_first_commit(project_path, parameters.gitlab_repo)

        install_project(project_path)

        cli.draw_line()
        cli.positive_feedback("New project '{}' installed successfully".format(parameters.project_name))
        cli.positive_feedback(
            "Please make sure by typing 'source activate.sh' and '{}' in the console".format(parameters.project_name))
        cli.give_hint("type 'pyqt-manager --help' to see more workflows.")
        cli.give_hint("launch PyCharm from the project folder to start working - "
                      "remember to type 'source activate.sh' in PyCharm terminal too")
        cli.draw_line()

    except Exception as e:
        cli.negative_feedback("A fatal error occurred: {}".format(e))
        # Try a quick cleanup
        if project_path:
            if parameters.interactive:
                answer = cli.handle_failure("Do you want to clean up what was created so far? "
                                            "This will delete the folder {}. (yes/no)".format(project_path))
                if answer == "y" or answer == "yes":
                    cli.negative_feedback("Cleaning up...")
                    shutil.rmtree(project_path, ignore_errors=True)
            elif parameters.cleanup_on_failure:
                cli.negative_feedback("Cleaning up...")
                shutil.rmtree(project_path, ignore_errors=True)
        cli.negative_feedback("Exiting\n")


def gather_setup_information(parameters: argparse.Namespace) -> argparse.Namespace:
    """
    Collects the information from the user. Might be interactive or not,
    depending on the user settings and the validation outcome.
    :param parameters: CLI parameters
    :return: the validated and updated CLI arguments
    """
    project_name_validator = re.compile("^[a-z0-9-]+$")
    parameters.project_name = utils.validate_as_arg_or_ask(
        cli_value=parameters.project_name,
        validator=lambda v: project_name_validator.match(v),
        question="Please enter your \033[0;33mproject's name\033[0;m:",
        neg_feedback="The project name can contain only lowercase letters, numbers and dashes.",
        pos_feedback="The project name is set to: \033[0;32m{}\033[0;m",
        interactive=parameters.interactive
    )
    parameters.project_desc = utils.validate_as_arg_or_ask(
        cli_value=parameters.project_desc,
        validator=lambda v: v != "" and "\"" not in v,
        question="Please enter a \033[0;33mone-line description\033[0;m of your project:",
        neg_feedback="The project description cannot contain the character \".",
        pos_feedback="The project description is set to: \033[0;32m{}\033[0;m",
        interactive=parameters.interactive
    )
    parameters.project_author = utils.validate_as_arg_or_ask(
        cli_value=parameters.project_author,
        validator=lambda v: v != "" and "\"" not in v,
        question="Please enter the project's \033[0;33mauthor name\033[0;m:",
        neg_feedback="The author name cannot contain the character \".",
        pos_feedback="The project author name is set to: \033[0;32m{}\033[0;m",
        interactive=parameters.interactive
    )
    author_email_validator = re.compile("[a-zA-Z0-9._%+-]+@cern.ch")  # TODO support email lists!
    parameters.author_email = utils.validate_as_arg_or_ask(
        cli_value=parameters.author_email,
        validator=lambda v: author_email_validator.match(v),
        question="Please enter the author's \033[0;33mCERN email address\033[0;m:",
        neg_feedback="Invalid CERN email.",
        pos_feedback="The project author's email name is set to: \033[0;32m{}\033[0;m",
        interactive=parameters.interactive
    )
    parameters.base_path = utils.validate_as_arg_or_ask(
        cli_value=parameters.project_path,
        validator=lambda v: (v == "." or os.path.isdir(v)),
        question="Please type the \033[0;33mpath\033[0;m where to create the new project, or type '.' to create it "
                 "in the current directory ({}):".format(os.getcwd()),
        neg_feedback="Please provide an existing folder.",
        pos_feedback="The project will be created under \033[0;32m{}\033[0;m".format(
            os.path.join("{}", parameters.project_name)),
        interactive=parameters.interactive
    )
    if parameters.base_path == '.':
        parameters.base_path = os.getcwd()

    repo_validator_ssh = re.compile("^ssh://git@gitlab.cern.ch:7999/[a-zA-Z0-9_%-]+/[a-zA-Z0-9_%/-]+.git$")
    repo_validator_https = re.compile("^https://gitlab.cern.ch/[a-zA-Z0-9_%-]+/[a-zA-Z0-9_%/-]+.git$")
    repo_validator_kerb = re.compile("^https://:@gitlab.cern.ch:8443/[a-zA-Z0-9_%-]+/[a-zA-Z0-9_%/-]+.git$")
    # parameters.gitlab_repo = None
    if parameters.gitlab:
        parameters.gitlab_repo = utils.validate_as_arg_or_ask(
            cli_value=parameters.gitlab_repo,
            validator=lambda v: (v is not None and (
                                 v == "" or
                                 v == "default" or
                                 v == "no-gitlab" or
                                 repo_validator_https.match(v) or
                                 repo_validator_ssh.match(v) or
                                 repo_validator_kerb.match(v))),
            question="Press ENTER to create a GitLab repository for your project under 'bisw-python', or enter your "
                     "existing GitLab repository address here (or type 'no-gitlab' to keep your repository local):",
            neg_feedback="Invalid GitLab repository URL.",
            pos_feedback="The project GitLab repository address is set to: \033[0;32m{}\033[0;m",
            hints=("copy the address from the Clone button, choosing the protocol you prefer (HTTPS, SSH, KRB5)", ),
            interactive=parameters.interactive
        )
        if parameters.gitlab_repo == 'no-gitlab':
            parameters.gitlab_repo = None
            parameters.gitlab = False
        if parameters.gitlab_repo == '' or parameters.gitlab_repo == 'default':
            parameters.gitlab_repo = "default"

    parameters.demo = utils.validate_demo_flags(parameters.force_demo, parameters.demo, parameters.interactive)

    return parameters


def check_path_is_available(project_path: str, interactive: bool = True, overwrite: bool = False) -> None:
    """
    Makes sure there is no folder with the name of the new project and if so ask the user and act accordingly.
    :param project_path: path to the new project
    :param interactive: whether the use should be asked what to do if the path exist
    :param overwrite: whether to automatically overwrite the existing folder
    """
    if os.path.exists(project_path):
        if overwrite:
            cli.list_subtask("Overwriting folder {}".format(project_path))
            shutil.rmtree(project_path)
        elif not interactive:
            raise OSError("Directory '{}' already exists.".format(project_path))
        else:
            answer = cli.handle_failure("A folder called '{}' already exists. ".format(project_path) +
                                        "Do you want to overwrite it? (yes/no)")
            if answer == "yes" or answer == "y":
                cli.list_subtask("Overwriting existing folder")
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


def download_template(project_path: str, clone_protocol: str, get_demo: bool, interactive: bool = True) -> None:
    """
    Downloads the template code from its GitLab repository
    :param project_path: Where to clone the template (folder must not exists)
    :param clone_protocol: use HTTPS, SSH or Kerberos
    :param get_demo: Clone the template with the demo application or without.
    :param interactive: Whether the code is allowed to ask the user interactively on how to proceed
    """
    if clone_protocol == 'https':
        template_url = 'https://gitlab.cern.ch/bisw-python/be-bi-pyqt-template.git'
    elif clone_protocol == 'kerberos':
        template_url = 'https://:@gitlab.cern.ch:8443/bisw-python/be-bi-pyqt-template.git'
    elif clone_protocol == 'ssh':
        template_url = 'ssh://git@gitlab.cern.ch:7999/bisw-python/be-bi-pyqt-template.git'
    else:
        raise ValueError("Clone protocol not recognized: {}".format(clone_protocol))

    if get_demo:
        git_command = ['clone', template_url, project_path]
    else:
        git_command = ['clone', '--single-branch', '--branch', 'no-demo', template_url,
                       project_path]
    utils.invoke_git(
        parameters=git_command,
        cwd=os.getcwd(),
        allow_retry=interactive,
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
                if filename.split(".")[-1] in ["py", "md", "ui", "qrc", "yml", "gitignore", "sh", "in"]:
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
                    project_email: str, gitlab_repo: str) -> None:
    """
    Generate a README with the invariant informations, like how to install, run tests, debug, etc...
    :param project_path: path to the project folder
    :param project_name: name of the project
    :param project_desc: description of the project
    :param project_author: name of the project's author
    :param project_email: email of the project's author, or support email
    :param gitlab_repo: the project's GitLab repo, if given
    """
    project_name_capitals = project_name.replace("-", " ").title()
    try:
        os.remove(os.path.join(project_path, "README.md"))
        os.rename(os.path.join(project_path, "README-template.md"), os.path.join(project_path, "README.md"))
        readme = os.path.join(project_path, "README.md")
        with open(readme) as f:
            s = f.read()
        if not gitlab_repo:
            gitlab_repo = "<the project's GitLab repo URL>.git"
        s = s.replace("https://:@gitlab.cern.ch:8443/cern-username/project-name.git", gitlab_repo)
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
    # In most cases, the failure is due to .git not existing.
    # In any case, if the failure is due to something else, most likely git will fail right after.
    shutil.rmtree("{}/.git".format(project_path), ignore_errors=True)
    utils.invoke_git(
        parameters=['init'],
        cwd=project_path,
        allow_retry=False,
        neg_feedback="Failed to init the repo in the project folder."
    )
    utils.invoke_git(
        parameters=['add', '--all'],
        cwd=project_path,
        allow_retry=False,
        neg_feedback="Failed to stage the template."
    )
    utils.invoke_git(
        parameters=['commit', '-m', 'Initial commit ' +
                    '(from bipy-gui-manager https://gitlab.cern.ch/bisw-python/bipy_gui_manager )'],
        cwd=project_path,
        allow_retry=False,
        neg_feedback="Failed to commit the template."
    )


def create_gitlab_repository(project_name: str, project_desc: str):
    """
    Create a GitLab repo under bisw-python
    :param project_name: Name of the project

    Token for szanzott = zznsVsiahNkpY1PBEZJ8
    curl -d "name=test-gitlab-api"  https://gitlab.cern.ch/api/v4/projects?private_token=zznsVsiahNkpY1PBEZJ8
    """
    url = 'https://gitlab.cern.ch/api/v4/projects?private_token=zznsVsiahNkpY1PBEZJ8'
    post_fields = {'name': project_name, 'description': project_desc}  # Set POST fields here
    request = Request(url, data=urlencode(post_fields).encode())
    data = json.loads(urlopen(request).read().decode())

    # The avatar setting honestly is not critical: if it fails, amen
    try:
        avatar_path = os.path.join(os.path.dirname(__file__), "resources", "PyQt-logo-gray.png")
        url = 'https://gitlab.cern.ch/api/v4/projects/{}'.format(data['id'])
        avatar = {'avatar': (avatar_path, open(avatar_path, 'rb'), 'multipart/form-data')}
        auth_header = {'PRIVATE-TOKEN': 'zznsVsiahNkpY1PBEZJ8'}
        requests.put(url, files=avatar, headers=auth_header)
    except Exception as e:
        print("  - Avatar upload failed: {}.".format(e))


def push_first_commit(project_path: str, gitlab_repo: str) -> None:
    """
    Adds a remote to the Git repo and pushes the first commit
    :param project_path: Path to the project root
    :param gitlab_repo: GitLab repo to push to
    """
    utils.invoke_git(
        parameters=['remote', 'add', 'origin', gitlab_repo],
        cwd=project_path,
        allow_retry=False,
        neg_feedback="Failed to add the remote on the project's local repo."
    )
    # Check for repository existence
    utils.invoke_git(
        parameters=['ls-remote'],
        cwd=project_path,
        allow_retry=False,
        neg_feedback="Seems like {} is not an existing and empty GitLab repository. ".format(gitlab_repo) +
                     "The repository should EXIST and be EMPTY at this stage. \n" +
                     "You can create the repo yourself and then pass the link with the --repo flag." +
                     "If you think this is a bug, please report it to the maintainers."
    )
    utils.invoke_git(
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
    shutil.copy(os.path.join(os.path.dirname(__file__), "resources", "install-project.sh"), script_temp_location)
    # Execute it (create venvs and install folder in venv)
    os.chmod(script_temp_location, 0o777)
    current_dir = os.getcwd()
    os.chdir(project_path)
    error = os.WEXITSTATUS(os.system("source ./.tmp.sh"))
    os.chdir(current_dir)
    # Remove temporary script
    os.remove(script_temp_location)
    # Render error if present
    if error:
        cli.negative_feedback("New project failed to install: {}.".format(error))
        cli.negative_feedback("Please execute 'source activate.sh' and 'pip install -e .'"
                              "in the project's root and, if it fails, send the log to the maintainers.")
        raise OSError("New project failed to install: {}.".format(error))
