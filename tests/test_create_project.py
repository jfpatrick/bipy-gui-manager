import os
import time
import pytest
from bipy_gui_manager.create_project import create_project

from .conftest import create_project_parameters, create_template_files


# ###############################
# #      Create Project         #
# ###############################
def test_create_project_defaults_all_in_flags(monkeypatch, tmpdir, mock_git, mock_gitlab, mock_phonebook):
    # Runs the entire script mocking only the necessary
    # all params come from CLI and should succeed, even though interactive=True
    params = create_project_parameters(path=tmpdir, name="test-project", desc="That's a test project!",
                                       author="me", repo_type="test", clone_protocol="https", gitlab_token="fake-token",
                                       upload_protocol="https", gitlab=True, crash=True)
    create_project.create_project(params)


def test_create_project_handles_exceptions_ask_cleanup(monkeypatch, tmpdir, mock_git, mock_gitlab, mock_phonebook):
    # Check if it fails in a controlled way and asks the user whether to cleanup
    params = create_project_parameters(path=tmpdir, name="test-project", desc="That's a test project!",
                                       author="me", repo_type="test", clone_protocol="https", gitlab_token="fake-token",
                                       upload_protocol="https", gitlab=True, crash=False, interactive=True)
    def fail(*args, **kwargs):
        raise AttributeError("Imagine this function fails...")
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.get_template', fail)

    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    with pytest.raises(ZeroDivisionError):
        create_project.create_project(params)


def test_create_project_handles_exceptions_cleanup_no(monkeypatch, tmpdir, mock_git, mock_gitlab, mock_phonebook):
    # Check if it fails in a controlled way and asks the user whether to cleanup
    params = create_project_parameters(path=tmpdir, name="test-project", desc="That's a test project!",
                                       author="me", repo_type="test", clone_protocol="https",
                                       gitlab_token="fake-token",
                                       upload_protocol="https", gitlab=True, crash=False, interactive=True)
    def fail(*args, **kwargs):
        tmpdir.mkdir("test-project")
        raise AttributeError("Imagine this function fails...")
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.get_template', fail)

    monkeypatch.setattr('builtins.input', lambda _: "no")
    create_project.create_project(params)
    time.sleep(0.1)
    assert os.path.isdir(os.path.join(tmpdir, "test-project"))


def test_create_project_handles_exceptions_cleanup_yes(monkeypatch, tmpdir, mock_git, mock_gitlab, mock_phonebook):
    # Check if it fails in a controlled way and asks the user whether to cleanup
    params = create_project_parameters(path=tmpdir, name="test-project", desc="That's a test project!",
                                       author="me", repo_type="test", clone_protocol="https",
                                       gitlab_token="fake-token",
                                       upload_protocol="https", gitlab=True, crash=False, interactive=True)
    def fail(*args, **kwargs):
        tmpdir.mkdir("test-project")
        raise AttributeError("Imagine this function fails...")
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.get_template', fail)

    monkeypatch.setattr('builtins.input', lambda _: "yes")
    create_project.create_project(params)
    time.sleep(0.1)
    assert not os.path.isdir(os.path.join(tmpdir, "test-project"))


# ###############################
# #        Get Template         #
# ###############################
def test_get_template_call_download_template(tmpdir, monkeypatch):
    # Make template folder
    template_folder = os.path.join(tmpdir, "template-folder")
    create_template_files(template_folder, "test-project")

    # Monkeypatch download_template
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.download_template',
                        lambda path, protocol: os.makedirs(os.path.join(tmpdir, path, "downloaded-files")))

    # Ensure it's calling download_template instead of copying
    project_path = os.path.join(tmpdir, "test_project")
    create_project.get_template(project_path=project_path,
                                clone_protocol="https",
                                template_path=None)

    assert os.path.isdir(project_path)  # Should exist in both cases
    assert not os.path.exists(os.path.join(project_path, "test_project"))  # Comes from the template folder
    assert os.path.isdir(os.path.join(tmpdir, project_path, "downloaded-files"))  # Monkeypatched download_template


def test_get_template_copy_from_path_valid(tmpdir, monkeypatch):
    # Make template folder
    template_folder = os.path.join(tmpdir, "template-folder")
    create_template_files(template_folder, "test-project")
    # Ensure it's copied if template_folder is not None
    project_path = os.path.join(tmpdir, "test-project")
    create_project.get_template(project_path=project_path,
                                clone_protocol="https",
                                template_path=template_folder)
    assert os.path.isdir(project_path)
    assert os.path.exists(os.path.join(project_path, "test_project"))
    with open(os.path.join(project_path, "README-template.md"), "r") as testfile:
        assert testfile.read() != ""
    with open(os.path.join(project_path, ".hidden_file"), "r") as testfile:
        assert testfile.read() == "Something hidden"
    assert not os.path.exists(os.path.join(project_path, "be_bi_pyqt_template"))


def test_get_template_copy_from_path_wrong(tmpdir, monkeypatch):
    # Ensure an error is raised
    project_path = os.path.join(tmpdir, "test_project")
    with pytest.raises(OSError):
        create_project.get_template(project_path=project_path,
                                    clone_protocol="https",
                                    template_path=os.path.join(tmpdir, "wrong_folder"))
    assert not os.path.isdir(project_path)


# ###############################
# #      Download Template      #
# ###############################
def test_download_template_kerberos(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "be-bi-pyqt-template")
    create_project.download_template(project_path, "kerberos")
    assert os.path.isdir(project_path)
    assert os.path.isdir(os.path.join(project_path, "be_bi_pyqt_template"))
    assert os.path.exists(os.path.join(project_path, "README-template.md"))


def test_download_template_ssh(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "be-bi-pyqt-template")
    create_project.download_template(project_path, "ssh")
    assert os.path.isdir(project_path)
    assert os.path.isdir(os.path.join(project_path, "be_bi_pyqt_template"))
    assert os.path.exists(os.path.join(project_path, "README-template.md"))


def test_download_template_https(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "be-bi-pyqt-template")
    create_project.download_template(project_path, "https")
    assert os.path.isdir(project_path)
    assert os.path.isdir(os.path.join(project_path, "be_bi_pyqt_template"))
    assert os.path.exists(os.path.join(project_path, "README-template.md"))


def test_download_template_wrong_protocol(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "be-bi-pyqt-template")
    with pytest.raises(ValueError):
        create_project.download_template(project_path, "wrongprotocol")
    assert not os.path.isdir(project_path)


def test_download_template_custom_url(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "be-bi-pyqt-template")
    create_project.download_template(project_path, "", custom_url="custom_url")
    assert os.path.isdir(project_path)


# ###############################
# #     Apply Customizations    #
# ###############################
def test_apply_customizations_valid_template(tmpdir):
    project_path = os.path.join(tmpdir, "be-bi-pyqt-template")
    create_template_files(project_path, "be-bi-pyqt-template")
    assert os.path.isdir(os.path.join(tmpdir, "be-bi-pyqt-template"))
    assert os.path.isdir(os.path.join(tmpdir, "be-bi-pyqt-template", "be_bi_pyqt_template"))

    create_project.apply_customizations(project_path=project_path,
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
        ]
        for word in not_present:
            assert word not in content
        for word in present:
            assert word in content


def test_readme(tmpdir):
    project_path = os.path.join(tmpdir, "be-bi-pyqt-template")
    create_template_files(project_path, "be-bi-pyqt-template")

    create_project.generate_readme(project_path=project_path,
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
