import os
import pytest
import bipy_gui_manager.create_project.create_project as create_project_module

from .conftest import create_template_files


def test_git_init_and_push(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "test-project")
    create_template_files(project_path, "test-project", True)
    create_project_module.init_local_repo(project_path)
    create_project_module.push_first_commit(project_path, "https://gitlab.cern.ch/test-project.git")
