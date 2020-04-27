import os
import pytest
import bipy_gui_manager.create_project.create_project as create_project_module

from .conftest import create_template_files


def test_copy_folder_from_path_valid(tmpdir, monkeypatch):
    # Make template folder
    template_folder = os.path.join(tmpdir, "template-folder")
    create_template_files(template_folder, "test-project", True)
    # Ensure it's copied
    project_path = os.path.join(tmpdir, "test-project")
    create_project_module.copy_folder_from_path(template_folder, project_path)
    assert os.path.isdir(project_path)
    assert os.path.exists(os.path.join(project_path, "test_project"))
    with open(os.path.join(project_path, "README-template.md"), "r") as testfile:
        assert testfile.read() != ""
    with open(os.path.join(project_path, ".hidden_file"), "r") as testfile:
        assert testfile.read() == "Something hidden"
    with open(os.path.join(project_path, "test_project", "demo_code.py"), "r") as testfile:
        assert testfile.read() != ""
    assert not os.path.exists(os.path.join(project_path, "be_bi_pyqt_template"))


def test_copy_folder_from_path_wrong_template_path(tmpdir, monkeypatch):
    # Ensure an error is raised
    project_path = os.path.join(tmpdir, "test_project")
    with pytest.raises(OSError):
        create_project_module.copy_folder_from_path(os.path.join(tmpdir, "wrong_folder"), project_path)
    assert not os.path.isdir(project_path)


def test_apply_customizations_valid_template(tmpdir):
    project_path = os.path.join(tmpdir, "be-bi-pyqt-template")
    create_template_files(project_path, "be-bi-pyqt-template", True)
    assert os.path.isdir(os.path.join(tmpdir, "be-bi-pyqt-template"))
    assert os.path.isdir(os.path.join(tmpdir, "be-bi-pyqt-template", "be_bi_pyqt_template"))

    create_project_module.apply_customizations(project_path=project_path,
                                               project_name="test-project",
                                               project_desc="This is a test",
                                               project_author="Test author",
                                               project_email="test-email@cern.ch")
    assert os.path.isdir(project_path)
    assert os.path.isdir(os.path.join(project_path, "test_project"))
    assert not os.path.exists(os.path.join(project_path, "images"))
    assert os.path.exists(os.path.join(project_path, "README-template.md"))
    with open(os.path.join(project_path, "setup.py"), "r") as setup:
        content = setup.read()
        not_present = [
            "be-bi-pyqt-template",
            "be_bi_pyqt_template",
            "Sara Zanzottera",
            "sara.zanzottera@cern.ch",
            "BE BI PyQt Template",
            "BE BI PyQt Template Code"
        ]
        present = [
            "test-project",
            "Test author",
            "test-email@cern.ch",
            "This is a test",
            "0.0.1.dev1",
            "setup",
            "REQUIREMENTS",
            "pyqt5",
            "pytest",
        ]
        for word in not_present:
            assert word not in content
        for word in present:
            assert word in content


def test_readme(tmpdir):
    project_path = os.path.join(tmpdir, "be-bi-pyqt-template")
    create_template_files(project_path, "be-bi-pyqt-template", True)

    create_project_module.generate_readme(project_path=project_path,
                                          project_name="test-project",
                                          project_desc="This is a test",
                                          project_author="Test author",
                                          project_email="test-email@cern.ch",
                                          gitlab_repo="https://gitlab.cern.ch/test-project.git")

    with open(os.path.join(project_path, "README.md"), "r") as readme:
        content = readme.readlines()
        assert content == [
            "Test Project\n",
            "This is a test\n",
            "test-project\n",
            "test_project\n",
            "test-email@cern.ch\n",
            "Test author\n",
            "https://gitlab.cern.ch/test-project.git\n",
            "Something that does not change"
        ]
