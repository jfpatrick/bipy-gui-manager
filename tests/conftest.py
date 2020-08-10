import os
import pytest
from argparse import Namespace
from pyphonebook import PhoneBookEntry


@pytest.fixture
def mock_cwd(tmpdir, monkeypatch):
    monkeypatch.setattr('os.getcwd', lambda: str(tmpdir))


def mock_phonebook_entry(i):
    if i == "me":
        phonebook_entry = PhoneBookEntry("")
        phonebook_entry.login_name = "me"
        phonebook_entry.full_name = ["Test User"]
        phonebook_entry.email = ["test.email@cern.ch"]
        return phonebook_entry, True
    return None, False


@pytest.fixture()
def mock_phonebook(monkeypatch):
    monkeypatch.setattr('bipy_gui_manager.create_project.validation.validate_cern_id', mock_phonebook_entry)


@pytest.fixture
def mock_git(monkeypatch, mock_cwd):
    monkeypatch.setattr('bipy_gui_manager.utils.version_control.invoke_git', mock_git_invocation)


@pytest.fixture
def mock_gitlab(monkeypatch, mock_cwd):
    monkeypatch.setattr('bipy_gui_manager.utils.version_control.authenticate_on_gitlab', mock_gitlab_auth)
    monkeypatch.setattr('bipy_gui_manager.utils.version_control.post_to_gitlab',
                        lambda *a, **k: {"id": "00000"})


def create_project_parameters(path=None, name=None, desc=None, author=None, repo_type=None,
                              clone_protocol="https", upload_protocol="https", gitlab=True,
                              gitlab_token=None, interactive=True, overwrite=False, cleanup_on_failure=False,
                              template_path=None, template_url=None, crash=True, verbose=False, gitlab_space=""):
    args = Namespace(
        base_path=path,
        project_name=name,
        project_desc=desc,
        project_author=author,
        gitlab_repo=repo_type,
        clone_protocol=clone_protocol,
        upload_protocol=upload_protocol,
        gitlab=gitlab,
        gitlab_token=gitlab_token,
        interactive=interactive,
        overwrite=overwrite,
        template_path=template_path,
        cleanup_on_failure=cleanup_on_failure,
        crash=crash,
        verbose=verbose,
        gitlab_space=gitlab_space,
        template_url=template_url
    )
    return args


def create_template_files(project_path, project_name):
    # Make folders
    template_module = project_name.replace("-", "_")
    os.makedirs(os.path.join(project_path, template_module))
    os.makedirs(os.path.join(project_path, "images"))

    # Write hidden file -  to ensure everything is copied over at need
    with open(os.path.join(project_path, ".hidden_file"), "w") as template:
        template.write("Something hidden")

    # Write setup.py -  to test the customizations
    with open(os.path.join(project_path, "setup.py"), "w") as readme:
        readme.write(
            """
from setuptools import setup
REQUIREMENTS = {
    'core': [  ],
    'test': [  ],
}
setup(
    name='be-bi-pyqt-template', 
    version="0.0.1.dev1", 
    author="Sara Zanzottera", 
    author_email="sara.zanzottera@cern.ch", 
    description="BE BI PyQt Template Code", 
    long_description="LONG_DESCRIPTION", 
    install_requires=REQUIREMENTS['core'], 
    entry_points={ 
        'console_scripts': [ 
            'be-bi-pyqt-template=be_bi_pyqt_template.main:main' 
        ] 
    }
) """
        )
    # Write README -  to test the customizations
    with open(os.path.join(project_path, "README.md"), "w") as _:
        pass
    with open(os.path.join(project_path, "README-template.md"), "w") as readme:
        readme.writelines([
            "Project Name\n",
            "_Here goes the project description_\n",
            "project-name\n",
            "project_name\n",
            "author@cern.ch\n",
            "the project author\n",
            "https://:@gitlab.cern.ch:8443/cern-username/project-name.git\n",
            "Something that does not change"
        ])


def mock_git_invocation(parameters, cwd, neg_feedback):
    """
    Used to mock the invoke_git function, which relies on calling system Git through subprocess.
    """
    # Only the clone operation really has some visible effect
    if 'clone' in parameters:
        project_path = parameters[-1]
        project_name = "be_bi_pyqt_template"  #project_path.split(os.path.sep)[-1]
        create_template_files(project_path, project_name)
    return f"mock call with parameters {parameters}", ""


def mock_gitlab_auth(username, password):
    if username == "me":
        return True
    return False


