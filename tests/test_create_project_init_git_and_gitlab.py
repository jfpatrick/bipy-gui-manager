import os
import io
import pytest
import bipy_gui_manager.create_project.create_project as create_project_module

from .conftest import create_template_files


def test_git_init_and_push(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "test-project")
    create_template_files(project_path, "test-project", True)
    create_project_module.init_local_repo(project_path)
    create_project_module.push_first_commit(project_path, "https://gitlab.cern.ch/test-project.git")


def test_create_gitlab_repo_username_password(monkeypatch):
    try:
        monkeypatch.setattr('requests.put', lambda *args, **kwargs: '')
    except ModuleNotFoundError:
        # requests is not installed in the test environment
        pass
    monkeypatch.setattr('bipy_gui_manager.create_project.vc_utils.post_to_gitlab', lambda *args, **kwargs: "")
    monkeypatch.setattr('bipy_gui_manager.create_project.vc_utils.authenticate_on_gitlab', lambda *args, **kwargs: 1/0)
    with pytest.raises(ZeroDivisionError):
        create_project_module.create_gitlab_repository("test-project", "A test project", auth_token=None,
                                                       username="test-user", password="garbagepassword")


def test_create_gitlab_repo_auth_token(monkeypatch):
    try:
        monkeypatch.setattr('requests.put', lambda *args, **kwargs: '')
    except ModuleNotFoundError:
        # requests is not installed in the test environment
        pass
    monkeypatch.setattr('bipy_gui_manager.create_project.vc_utils.post_to_gitlab', lambda *args, **kwargs: "")
    monkeypatch.setattr('bipy_gui_manager.create_project.vc_utils.authenticate_on_gitlab', lambda *args, **kwargs: 1/0)
    create_project_module.create_gitlab_repository("test-project", "A test project",
                                                   username=None, password=None, auth_token="auth-token")

