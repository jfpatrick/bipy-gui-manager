import os
import pytest
import bipy_gui_manager.create_project.create_project as create_project_module

from .conftest import create_project_parameters


def test_create_project_defaults(monkeypatch):
    # Testing only that it won't fail with the defaults
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.gather_setup_information', lambda *a, **k:
        [""]*6 + [parameters])
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.check_path_is_available', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.copy_folder_from_path', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.download_template', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.apply_customizations', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.generate_readme', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.init_local_repo', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.push_first_commit', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.install_project', lambda *a, **k: True)
    create_project_module.create_project(parameters)


def test_create_project_copy_template(monkeypatch):
    # Testing only that it won't fail by taking this option
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git", template_path="here")
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.gather_setup_information', lambda *a, **k:
    [""] * 6 + [parameters])
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.check_path_is_available', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.copy_folder_from_path', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.download_template', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.apply_customizations', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.generate_readme', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.init_local_repo', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.push_first_commit', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.install_project', lambda *a, **k: True)
    create_project_module.create_project(parameters)


def test_create_project_handle_errors(monkeypatch):
    # Won't raise this error, will handle it internally
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.gather_setup_information', lambda *a, **k: 1/0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    create_project_module.create_project(parameters)
