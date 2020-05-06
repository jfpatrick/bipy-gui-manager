from typing import Optional
import os
import argparse
import shutil
from bipy_gui_manager import cli_utils as cli
from bipy_gui_manager.create_project import project_info, version_control


def create_project(parameters: argparse.Namespace):
    """
    Main 'script' for the creation process. Calls, in order, all the functions required to setup a project properly.
    :param parameters: the parameters passed through the CLI
    :return: None, but creates a project according to the information gathered.
    """
    # Initially defined here to be available for an eventual cleanup procedure, if something goes wrong
    valid_project_data = {}
    try:
        cli.print_welcome()

        print("  Setup: \n")
        valid_project_data = project_info.collect(parameters)

        cli.draw_line()
        print("  Installation:\n")

        get_template(project_path=valid_project_data["project_path"],
                     clone_protocol=parameters.clone_protocol,
                     demo=valid_project_data["demo"],
                     template_path=valid_project_data.get("template_path", None))

        apply_customizations(project_path=valid_project_data["project_path"],
                             project_name=valid_project_data["project_name"],
                             project_desc=valid_project_data["project_desc"],
                             project_author=valid_project_data["author_full_name"],
                             project_email=valid_project_data["author_email"],)

        generate_readme(project_path=valid_project_data["project_path"],
                        project_name=valid_project_data["project_name"],
                        project_desc=valid_project_data["project_desc"],
                        project_author=valid_project_data["author_full_name"],
                        project_email=valid_project_data["author_email"],
                        gitlab_repo=valid_project_data.get("repo_url", None))

        setup_version_control(project_path=valid_project_data["project_path"],
                              gitlab=parameters.gitlab,
                              project_name=valid_project_data["project_name"],
                              project_desc=valid_project_data["project_desc"],
                              gitlab_token=valid_project_data.get("author_token", None),
                              repo_type=valid_project_data.get("repo_type", "test"),
                              repo_url=valid_project_data.get("repo_url", None))

        install_project(project_path=valid_project_data["project_path"])

        cli.draw_line()
        cli.positive_feedback("New project '{}' installed successfully.\033[1A".format(
            valid_project_data["project_name"]), newline=False)
        cli.draw_line()

        what_you_see: str
        if valid_project_data["demo"]:
            what_you_see = "a window with the demo app inside"
        else:
            what_you_see = "an empty window"

        cli.positive_feedback("What now?\n\n"
                              "Your project now lives under '{}'. \n".format(valid_project_data["project_path"]) +
                              "To make sure the installation was successful, you should move into that \nfolder and " +
                              "type the following commands:\n" +
                              "   > source activate.sh        (activates acc-py and your virtual env)\n"
                              "   > {}        (launches your PyQt application)\n".format(
                                  valid_project_data["project_name"]) +
                              "You should see {}. \n".format(what_you_see) +
                              "If you don't, or you see and error of some kind, please report it to us.\n\n" +
                              "Once this is done, you can start working on your new app. If you have \n" +
                              "already acc-py active in you shell, type 'charm' from your project's \n"+
                              "directory: this will launch PyCharm and make it load the right project \n"+
                              "directly. \n"+
                              "If this doesn't work, try launching PyCharm manually by executing \n" +
                              "'/acc/local/share/python/pycharm/pycharm-community-2019.2.3/bin/pycharm.sh'\n"
                              "or contact acc-py support for help.\n\n" +
                              "Remember also to activate your virtual env with 'source activate.sh'\n"+
                              "every time you start working.\n\n"
                              "Happy development!\033[1A", newline=False)
        cli.draw_line()

    except Exception as e:
        cli.negative_feedback("A fatal error occurred: {}".format(e))

        if parameters.crash:
            # Just crash and show the stacktrace
            raise e

        if valid_project_data and "project_path" in valid_project_data.keys():
            # Try a quick cleanup
            cleanup_on_failure(project_path=valid_project_data["project_path"],
                               interactive=parameters.interactive,
                               force_cleanup=parameters.cleanup_on_failure)

        cli.negative_feedback("Exiting\n")


def get_template(project_path, clone_protocol, demo, template_path: Optional[str] = None) -> None:
    """
    Retrieves the template code for the new project.
    :param project_path: Where to create the new project
    :param clone_protocol: Which protocol to use to clone the template from GitLab (https, ssh, kerberos)
    :param demo: whether to include the demo in the project
    :param template_path: If given, points to a local path to copy the content of, instead of cloning from GitLab
    :return: Nothing, but creates a folder with the template code
    """
    if template_path is not None:
        cli.positive_feedback("Copying the template from {}".format(template_path), newline=False)
        shutil.copytree(template_path, project_path)
        # Change this into a os.rename operation?
        shutil.move(template_path, os.path.join(os.path.dirname(template_path), os.path.basename(project_path)))
    else:
        cli.positive_feedback("Downloading the template from GitLab", newline=False)
        download_template(project_path, clone_protocol, demo)


def download_template(project_path: str, clone_protocol: str, get_demo: bool) -> None:
    """
    Downloads the template code from its GitLab repository
    :param project_path: Where to clone the template (folder must not exists)
    :param clone_protocol: use HTTPS, SSH or Kerberos
    :param get_demo: Clone the template with the demo application or without.
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

    version_control.invoke_git(
        parameters=git_command,
        cwd=os.getcwd(),
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
    cli.positive_feedback("Applying customizations", newline=False)

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
    cli.positive_feedback("Preparing README", newline=False)

    project_name_capitals = project_name.replace("-", " ").title()
    project_name_underscores = project_name.replace("-", "_")
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
        s = s.replace("project_name", project_name_underscores)
        s = s.replace("Project Name", project_name_capitals)
        s = s.replace("_Here goes the project description_", project_desc)
        s = s.replace("the project author", project_author)
        s = s.replace("author@cern.ch", project_email)
        with open(readme, "w") as f:
            f.write(s)

        cli.give_hint("check the README for typos and complete it with a more in-depth description of your project.")

    except Exception as e:
        cli.negative_feedback("Failed to generate README")
        raise e


def setup_version_control(project_path: str, gitlab: bool, project_name: Optional[str], project_desc: Optional[str],
                          gitlab_token: Optional[str], repo_type: Optional[str], repo_url: Optional[str]) -> None:
    """
    Sets up the local and remote version control for the project.
    :param project_path: Path to the new project
    :param project_name: Name of the project
    :param project_desc: Description of the project
    :param gitlab: True if the project needs to be uploaded to GitLab
    :param gitlab_token: Authentication token to login into GitLab
    :param repo_type: Repository URL
    :return:
    """
    cli.positive_feedback("Setting up local Git repository", newline=False)

    # In most cases, the failure is due to .git not existing.
    # In any case, if the failure is due to something else, most likely git will fail right after.
    shutil.rmtree("{}/.git".format(project_path), ignore_errors=True)

    version_control.init_local_repo(project_path)

    if gitlab:
        cli.positive_feedback("Creating repository on GitLab", newline=False)
        version_control.create_gitlab_repository(repo_type, project_name, project_desc, auth_token=gitlab_token)

        cli.positive_feedback("Uploading project on GitLab", newline=False)
        version_control.push_first_commit(project_path, repo_url)


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


def cleanup_on_failure(project_path: str, interactive: bool, force_cleanup: bool) -> None:
    """
    In case of failure, this function is called to verify whether the user wants to
    do a cleanup of the folders created so far, and cleans up if positive.
    :param project_path: Folder to delete
    :param interactive: Whether the script can ask the user interactively
    :param force_cleanup: Just cleanup without asking
    :return: Nothing, but might delete the project folder.
    """
    if force_cleanup:
        cli.negative_feedback("Cleaning up...")
        shutil.rmtree(project_path, ignore_errors=True)
    elif interactive:
        answer = cli.handle_failure("Do you want to clean up what was created so far? "
                                    "This will delete the folder {}. (yes/no)".format(project_path))
        if answer == "y" or answer == "yes":
            cli.negative_feedback("Cleaning up...")
            shutil.rmtree(project_path, ignore_errors=True)
