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


def mock_git_invocation(parameters, cwd, allow_retry=False, neg_feedback="Test exception"):
    """
    Used to mock the invoke_git function, which relies on calling system Git through subprocess.
    """
    # Only the clone operation really has some visible effect
    if 'clone' in parameters:
        project_path = parameters[-1]
        project_name = project_path.split(os.path.sep)[-1]
        project_module = project_name.replace("-", "_")
        os.makedirs(os.path.join(project_path, project_module))
        with open(os.path.join(project_path, "README.md"), "w") as readme:
            readme.writelines([
                "Project Name",
                "Here goes the project description",
                "project-name",
                "author@cern.ch",
                "the project author",
                "https://:@gitlab.cern.ch:8443/cern-username/project-name.git"
            ])
        if "no-demo" not in parameters:
            with open(os.path.join(project_path, project_module, "demo_code.py"), "w") as demo:
                demo.write("raise ValueError('Somebody called this script??')")





