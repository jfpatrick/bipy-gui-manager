import os
import pytest
from argparse import Namespace
from pathlib import Path

from bipy_gui_manager.release import release
from bipy_gui_manager.utils import version_control as vcs

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
    assert not release.is_python_project(tmpdir / 'nonexisting')
    assert not release.is_python_project(tmpdir)
    with open(tmpdir / 'setup.py', 'w') as f:
        f.write("hello")
    assert release.is_python_project(tmpdir)


def test_get_entry_point(tmpdir):
    # FIXME once the original method is also fixed
    nested = tmpdir / 'nested' / 'project'
    os.makedirs(nested)
    assert release.get_entry_point(nested) == 'project'


def test_is_ready_to_deploy(tmpdir):
    pass


def test_release_empty_dir(project_dir, deploy_dir):
    release.release(Namespace(verbose=False))
    assert len(os.listdir(deploy_dir)) == 0


def test_release_dir_with_setup_only(project_dir, deploy_dir):
    with open(project_dir / 'setup.py', 'w') as f:
        f.write("hello")
    release.release(Namespace(verbose=False))
    assert len(os.listdir(deploy_dir)) == 0


def test_release_dir_with_git_only(project_dir, deploy_dir):
    vcs.invoke_git(['init'], cwd=project_dir)
    release.release(Namespace(verbose=False))
    assert len(os.listdir(deploy_dir)) == 0


def test_release_dir_with_setup_and_git(project_dir, deploy_dir):
    with open(project_dir / 'setup.py', 'w') as f:
        f.write("hello")
    vcs.invoke_git(['init'], cwd=project_dir)
    release.release(Namespace(verbose=False))
    assert len(os.listdir(deploy_dir)) == 0
