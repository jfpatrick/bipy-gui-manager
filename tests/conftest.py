import os
import pytest

@pytest.fixture
def mock_all_subtasks(monkeypatch):
    monkeypatch.setattr('be_bi_pyqt_project_manager.create_project.check_path_is_available', lambda *args, **kwargs: None)
    monkeypatch.setattr('be_bi_pyqt_project_manager.create_project.copy_folder_from_path', lambda *args, **kwargs: None)
    monkeypatch.setattr('be_bi_pyqt_project_manager.create_project.download_template', lambda *args, **kwargs: None)
    monkeypatch.setattr('be_bi_pyqt_project_manager.create_project.apply_customizations', lambda *args, **kwargs: None)
    monkeypatch.setattr('be_bi_pyqt_project_manager.create_project.generate_readme', lambda *args, **kwargs: None)
    monkeypatch.setattr('be_bi_pyqt_project_manager.create_project.init_local_repo', lambda *args, **kwargs: None)
    monkeypatch.setattr('be_bi_pyqt_project_manager.create_project.push_first_commit', lambda *args, **kwargs: None)
    monkeypatch.setattr('be_bi_pyqt_project_manager.create_project.install_project', lambda *args, **kwargs: None)
    # This one should never get called
    monkeypatch.setattr('be_bi_pyqt_project_manager.create_project.invoke_git', lambda *args, **kwargs: 1/0)
    yield


@pytest.fixture
def mock_git(tmpdir, monkeypatch):
    monkeypatch.setattr('os.getcwd', lambda: str(tmpdir))
    monkeypatch.setattr('be_bi_pyqt_project_manager.create_project.invoke_git', mock_git_invocation)


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





