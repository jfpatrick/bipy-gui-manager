import os
import pytest
import logging
from argparse import Namespace
from pathlib import Path

from bipy_gui_manager.deploy import deploy
from bipy_gui_manager.utils import version_control as vcs
from .conftest import create_template_files


@pytest.fixture()
def deploy_dir(tmpdir):
    deploy_dir = tmpdir / 'deploy'
    os.makedirs(deploy_dir)
    yield deploy_dir


@pytest.fixture()
def project_dir(tmpdir):
    project_dir = tmpdir / 'project'
    os.makedirs(project_dir)
    yield project_dir


def test_is_python_project(tmpdir):
    assert not deploy.is_python_project(tmpdir / 'nonexisting')
    assert not deploy.is_python_project(tmpdir)
    with open(tmpdir / 'setup.py', 'w') as f:
        f.write("hello")
    assert deploy.is_python_project(tmpdir)


def test_is_ready_to_deploy_conditions_met(project_dir, monkeypatch):
    vcs.invoke_git(['init'], cwd=project_dir)
    monkeypatch.setattr('bipy_gui_manager.deploy.deploy.vcs.get_remote_url',
                        lambda p: "https://gitlab.cern.ch/noexistinggroup/test.git")
    assert deploy.is_ready_to_deploy(project_dir)


def test_is_ready_to_deploy_not_master(project_dir, monkeypatch):
    vcs.invoke_git(['init'], cwd=project_dir)
    vcs.invoke_git(['checkout', '-b', 'test'], cwd=project_dir)
    monkeypatch.setattr('bipy_gui_manager.deploy.deploy.vcs.get_remote_url',
                        lambda p: "https://gitlab.cern.ch/noexistinggroup/test.git")
    assert not deploy.is_ready_to_deploy(project_dir)


def test_is_ready_to_deploy_no_remote(project_dir, monkeypatch):
    vcs.invoke_git(['init'], cwd=project_dir)
    assert not deploy.is_ready_to_deploy(project_dir)


def test_is_ready_to_deploy_dirty_folder(project_dir, monkeypatch):
    vcs.invoke_git(['init'], cwd=project_dir)
    with open(project_dir / 'file', 'w') as f:
        f.write("f")
    monkeypatch.setattr('bipy_gui_manager.deploy.deploy.vcs.get_remote_url',
                        lambda p: "https://gitlab.cern.ch/noexistinggroup/test.git")
    assert not deploy.is_ready_to_deploy(project_dir)


def test_release_empty_dir(project_dir, deploy_dir):
    deploy.deploy(Namespace(verbose=True, path=project_dir, debug=True, entry_point=None, operational=False))
    assert len(os.listdir(deploy_dir)) == 0


def test_release_dir_with_setup_only(project_dir, deploy_dir):
    with open(project_dir / 'setup.py', 'w') as f:
        f.write("hello")
    deploy.deploy(Namespace(verbose=True, path=project_dir, debug=True, entry_point=None, operational=False))
    assert len(os.listdir(deploy_dir)) == 0


def test_release_dir_with_git_only(project_dir, deploy_dir):
    vcs.invoke_git(['init'], cwd=project_dir)
    deploy.deploy(Namespace(verbose=True, path=project_dir, debug=True, entry_point=None, operational=False))
    assert len(os.listdir(deploy_dir)) == 0


def test_release_dir_with_setup_and_git(project_dir, deploy_dir):
    with open(project_dir / 'setup.py', 'w') as f:
        f.write("hello")
    vcs.invoke_git(['init'], cwd=project_dir)
    deploy.deploy(Namespace(verbose=True, path=project_dir, debug=True, entry_point=None, operational=False))
    assert len(os.listdir(deploy_dir)) == 0


@pytest.mark.skip("CI has no access to Acc-Py")
def test_release_dir_succeeds_with_real_repo_no_debug(project_dir, deploy_dir, monkeypatch):
    monkeypatch.setattr('bipy_gui_manager.deploy.deploy.vcs.get_remote_url',
                        lambda p: "https://:@gitlab.cern.ch:8443/bisw-python/be-bi-pyqt-template.git")
    monkeypatch.setattr('bipy_gui_manager.deploy.deploy.REPO_PATH', deploy_dir)
    create_template_files(project_dir, "project")
    vcs.init_local_repo(project_dir)

    deploy.deploy(Namespace(verbose=True, path=project_dir, debug=True, entry_point=None, operational=False))
    logging.debug(os.listdir(deploy_dir))
    # Acc-py creates a folder named as declared in setup.py
    assert os.path.exists(deploy_dir / "be-bi-pyqt-template")
