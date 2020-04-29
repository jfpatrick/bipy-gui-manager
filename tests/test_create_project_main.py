import os
import pytest
from bipy_gui_manager.create_project import create_project

from .conftest import create_project_parameters, create_template_files

#
# def test_create_project_defaults(monkeypatch):
#     # Testing only that it won't fail with the defaults
#     parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
#                                            repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
#     monkeypatch.setattr('bipy_gui_manager.create_project.create_project.gather_setup_information',
#                         lambda *a, **k: parameters)
#     monkeypatch.setattr('bipy_gui_manager.create_project.create_project.check_path_is_available', lambda *a, **k: True)
#     monkeypatch.setattr('bipy_gui_manager.create_project.create_project.copy_folder_from_path', lambda *a, **k: True)
#     monkeypatch.setattr('bipy_gui_manager.create_project.create_project.download_template', lambda *a, **k: True)
#     monkeypatch.setattr('bipy_gui_manager.create_project.create_project.apply_customizations', lambda *a, **k: True)
#     monkeypatch.setattr('bipy_gui_manager.create_project.create_project.generate_readme', lambda *a, **k: True)
#     monkeypatch.setattr('bipy_gui_manager.create_project.create_project.init_local_repo', lambda *a, **k: True)
#     monkeypatch.setattr('bipy_gui_manager.create_project.create_project.push_first_commit', lambda *a, **k: True)
#     monkeypatch.setattr('bipy_gui_manager.create_project.create_project.install_project', lambda *a, **k: True)
#     create_project.create_project(parameters)
#
#
# def test_create_project_copy_template(monkeypatch):
#     # Testing only that it won't fail by taking this option
#     parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
#                                            repo="ssh://git@gitlab.cern.ch:7999/user/project.git", template_path="here")
#     monkeypatch.setattr('bipy_gui_manager.create_project.create_project.gather_setup_information',
#                         lambda *a, **k: parameters)
#     monkeypatch.setattr('bipy_gui_manager.create_project.create_project.check_path_is_available', lambda *a, **k: True)
#     monkeypatch.setattr('bipy_gui_manager.create_project.create_project.copy_folder_from_path', lambda *a, **k: True)
#     monkeypatch.setattr('bipy_gui_manager.create_project.create_project.download_template', lambda *a, **k: True)
#     monkeypatch.setattr('bipy_gui_manager.create_project.create_project.apply_customizations', lambda *a, **k: True)
#     monkeypatch.setattr('bipy_gui_manager.create_project.create_project.generate_readme', lambda *a, **k: True)
#     monkeypatch.setattr('bipy_gui_manager.create_project.create_project.init_local_repo', lambda *a, **k: True)
#     monkeypatch.setattr('bipy_gui_manager.create_project.create_project.push_first_commit', lambda *a, **k: True)
#     monkeypatch.setattr('bipy_gui_manager.create_project.create_project.install_project', lambda *a, **k: True)
#     create_project.create_project(parameters)
#
#
# def test_create_project_handle_errors(monkeypatch):
#     # Won't raise this error, will handle it internally
#     monkeypatch.setattr('bipy_gui_manager.create_project.create_project.gather_setup_information', lambda *a, **k: 1/0)
#     parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
#                                            repo="ssh://git@gitlab.cern.ch:7999/user/project.git", crash=False)
#     create_project.create_project(parameters)


# ###############################
# #        Get Template         #
# ###############################
def test_get_template_call_download_template(tmpdir, monkeypatch):
    # Make template folder
    template_folder = os.path.join(tmpdir, "template-folder")
    create_template_files(template_folder, "test-project", True)

    # Monkeypatch download_template
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.download_template',
                        lambda path, protocol, demo: os.makedirs(os.path.join(tmpdir, path, "downloaded-files")))

    # Ensure it's calling download_template instead of copying
    project_path = os.path.join(tmpdir, "test_project")
    create_project.get_template(project_path=project_path,
                                clone_protocol="https",
                                demo=True,
                                template_path=None)

    assert os.path.isdir(project_path)  # Should exist in both cases
    assert not os.path.exists(os.path.join(project_path, "test_project"))  # Comes from the template folder
    assert os.path.isdir(os.path.join(tmpdir, project_path, "downloaded-files"))  # Monkeypatched download_template


def test_get_template_copy_from_path_valid(tmpdir, monkeypatch):
    # Make template folder
    template_folder = os.path.join(tmpdir, "template-folder")
    create_template_files(template_folder, "test-project", True)
    # Ensure it's copied if template_folder is not None
    project_path = os.path.join(tmpdir, "test-project")
    create_project.get_template(project_path=project_path,
                                clone_protocol="https",
                                demo=True,
                                template_path=template_folder)
    assert os.path.isdir(project_path)
    assert os.path.exists(os.path.join(project_path, "test_project"))
    with open(os.path.join(project_path, "README-template.md"), "r") as testfile:
        assert testfile.read() != ""
    with open(os.path.join(project_path, ".hidden_file"), "r") as testfile:
        assert testfile.read() == "Something hidden"
    with open(os.path.join(project_path, "test_project", "demo_code.py"), "r") as testfile:
        assert testfile.read() != ""
    assert not os.path.exists(os.path.join(project_path, "be_bi_pyqt_template"))


def test_get_template_copy_from_path_wrong(tmpdir, monkeypatch):
    # Ensure an error is raised
    project_path = os.path.join(tmpdir, "test_project")
    with pytest.raises(OSError):
        create_project.get_template(project_path=project_path,
                                    clone_protocol="https",
                                    demo=True,
                                    template_path=os.path.join(tmpdir, "wrong_folder"))
    assert not os.path.isdir(project_path)


# ###############################
# #      Download Template      #
# ###############################
def test_download_template_kerberos_no_demo(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "test-project")
    create_project.download_template(project_path, "kerberos", False)
    assert os.path.isdir(project_path)
    assert os.path.isdir(os.path.join(project_path, "test_project"))
    assert os.path.exists(os.path.join(project_path, "README-template.md"))


def test_download_template_kerberos_with_demo(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "test-project")
    create_project.download_template(project_path, "kerberos", True)
    assert os.path.isdir(project_path)
    assert os.path.isdir(os.path.join(project_path, "test_project"))
    assert os.path.exists(os.path.join(project_path, "README-template.md"))
    assert os.path.exists(os.path.join(project_path, "test_project", "demo_code.py"))
    with open(os.path.join(project_path, "test_project", "demo_code.py"), "r") as demo:
        assert demo.read() == "raise ValueError('Somebody called this script??')"


def test_download_template_ssh_no_demo(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "test-project")
    create_project.download_template(project_path, "ssh", False)
    assert os.path.isdir(project_path)
    assert os.path.isdir(os.path.join(project_path, "test_project"))
    assert os.path.exists(os.path.join(project_path, "README-template.md"))


def test_download_template_ssh_with_demo(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "test-project")
    create_project.download_template(project_path, "ssh", True)
    assert os.path.isdir(project_path)
    assert os.path.isdir(os.path.join(project_path, "test_project"))
    assert os.path.exists(os.path.join(project_path, "README-template.md"))
    assert os.path.exists(os.path.join(project_path, "test_project", "demo_code.py"))
    with open(os.path.join(project_path, "test_project", "demo_code.py"), "r") as demo:
        assert demo.read() == "raise ValueError('Somebody called this script??')"


def test_download_template_https_no_demo(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "test-project")
    create_project.download_template(project_path, "https", False)
    assert os.path.isdir(project_path)
    assert os.path.isdir(os.path.join(project_path, "test_project"))
    assert os.path.exists(os.path.join(project_path, "README-template.md"))


def test_download_template_https_with_demo(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "test-project")
    create_project.download_template(project_path, "https", True)
    assert os.path.isdir(project_path)
    assert os.path.isdir(os.path.join(project_path, "test_project"))
    assert os.path.exists(os.path.join(project_path, "README-template.md"))
    assert os.path.exists(os.path.join(project_path, "test_project", "demo_code.py"))
    with open(os.path.join(project_path, "test_project", "demo_code.py"), "r") as demo:
        assert demo.read() == "raise ValueError('Somebody called this script??')"


def test_download_template_wrong_protocol(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "test-project")
    with pytest.raises(ValueError):
        create_project.download_template(project_path, "wrongprotocol", True)
    assert not os.path.isdir(project_path)


def test_apply_customizations_valid_template(tmpdir):
    project_path = os.path.join(tmpdir, "be-bi-pyqt-template")
    create_template_files(project_path, "be-bi-pyqt-template", True)
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
