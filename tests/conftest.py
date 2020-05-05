import os
import pytest
from argparse import Namespace
from bipy_gui_manager.phonebook.phonebook import PhonebookEntry


@pytest.fixture
def mock_cwd(tmpdir, monkeypatch):
    monkeypatch.setattr('os.getcwd', lambda: str(tmpdir))


def mock_phonebook_entry(i):
    if i == "me":
        phonebook_entry = PhonebookEntry("")
        phonebook_entry.cern_id = "me"
        phonebook_entry.display_name = "Test User"
        phonebook_entry.emails = ["test.email@cern.ch"]
        return phonebook_entry, True
    return None, False


@pytest.fixture()
def mock_phonebook(monkeypatch):
    monkeypatch.setattr('bipy_gui_manager.create_project.validation.validate_cern_id', mock_phonebook_entry)


@pytest.fixture
def mock_git(tmpdir, monkeypatch, mock_cwd):
    monkeypatch.setattr('bipy_gui_manager.create_project.version_control.invoke_git', mock_git_invocation)


def create_project_parameters(demo=True, force_demo=True, path=".", name=None, desc=None, author=None,
                              repo_type=None, clone_protocol="https", upload_protocol="https", gitlab=True,
                              gitlab_token=None, interactive=True, overwrite=False,
                              template_path=None, crash=True):
    args = Namespace(
        demo=demo,
        force_demo=force_demo,
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
        crash=crash,
    )
    return args


def create_template_files(project_path, project_name, demo=True):
    # Make folders
    template_module = project_name.replace("-", "_")
    os.makedirs(os.path.join(project_path, template_module))
    os.makedirs(os.path.join(project_path, "images"))

    # Write hidden file -  to ensure everything is copied over at need
    with open(os.path.join(project_path, ".hidden_file"), "w") as template:
        template.write("Something hidden")

    # Write setup.py -  to test the customizations
    with open(os.path.join(project_path, "setup.py"), "w") as readme:
        readme.writelines([
            "REQUIREMENTS: dict = {",
            "    'core': [ \"pyqt5\", ],",
            "    'test': [ \"pytest\", ],",
            "}",
            "setup(",
            "    name='be-bi-pyqt-template', ",
            "    version=\"0.0.1.dev1\", ",
            "    author=\"Sara Zanzottera\", ",
            "    author_email=\"sara.zanzottera@cern.ch\", ",
            "    description=\"BE BI PyQt Template Code\", ",
            "    long_description=LONG_DESCRIPTION, ",
            "    install_requires=REQUIREMENTS['core'], ",
            "    entry_points={ 'console_scripts': [ 'be-bi-pyqt-template=be_bi_pyqt_template.main:main', ], },",
            ")",
        ])

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

    if demo:
        # Write demo file - to test demo selection
        with open(os.path.join(project_path, template_module, "demo_code.py"), "w") as demo:
            demo.write("raise ValueError('Somebody called this script??')")


def mock_git_invocation(parameters, cwd, allow_retry=False, neg_feedback="Test exception"):
    """
    Used to mock the invoke_git function, which relies on calling system Git through subprocess.
    """
    # Only the clone operation really has some visible effect
    if 'clone' in parameters:
        project_path = parameters[-1]
        project_name = project_path.split(os.path.sep)[-1]
        if 'no-demo' in parameters:
            demo = False
        else:
            demo = True
        create_template_files(project_path, project_name, demo=demo)





