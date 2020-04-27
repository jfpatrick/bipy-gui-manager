import os
import pytest
import bipy_gui_manager.create_project.create_project as create_project_module


def test_download_template_kerberos_no_demo(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "test-project")
    create_project_module.download_template(project_path, "kerberos", False)
    assert os.path.isdir(project_path)
    assert os.path.isdir(os.path.join(project_path, "test_project"))
    assert os.path.exists(os.path.join(project_path, "README-template.md"))


def test_download_template_kerberos_with_demo(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "test-project")
    create_project_module.download_template(project_path, "kerberos", True)
    assert os.path.isdir(project_path)
    assert os.path.isdir(os.path.join(project_path, "test_project"))
    assert os.path.exists(os.path.join(project_path, "README-template.md"))
    assert os.path.exists(os.path.join(project_path, "test_project", "demo_code.py"))
    with open(os.path.join(project_path, "test_project", "demo_code.py"), "r") as demo:
        assert demo.read() == "raise ValueError('Somebody called this script??')"


def test_download_template_ssh_no_demo(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "test-project")
    create_project_module.download_template(project_path, "ssh", False)
    assert os.path.isdir(project_path)
    assert os.path.isdir(os.path.join(project_path, "test_project"))
    assert os.path.exists(os.path.join(project_path, "README-template.md"))


def test_download_template_ssh_with_demo(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "test-project")
    create_project_module.download_template(project_path, "ssh", True)
    assert os.path.isdir(project_path)
    assert os.path.isdir(os.path.join(project_path, "test_project"))
    assert os.path.exists(os.path.join(project_path, "README-template.md"))
    assert os.path.exists(os.path.join(project_path, "test_project", "demo_code.py"))
    with open(os.path.join(project_path, "test_project", "demo_code.py"), "r") as demo:
        assert demo.read() == "raise ValueError('Somebody called this script??')"


def test_download_template_https_no_demo(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "test-project")
    create_project_module.download_template(project_path, "https", False)
    assert os.path.isdir(project_path)
    assert os.path.isdir(os.path.join(project_path, "test_project"))
    assert os.path.exists(os.path.join(project_path, "README-template.md"))


def test_download_template_https_with_demo(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "test-project")
    create_project_module.download_template(project_path, "https", True)
    assert os.path.isdir(project_path)
    assert os.path.isdir(os.path.join(project_path, "test_project"))
    assert os.path.exists(os.path.join(project_path, "README-template.md"))
    assert os.path.exists(os.path.join(project_path, "test_project", "demo_code.py"))
    with open(os.path.join(project_path, "test_project", "demo_code.py"), "r") as demo:
        assert demo.read() == "raise ValueError('Somebody called this script??')"


def test_download_template_wrong_protocol(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "test-project")
    with pytest.raises(ValueError):
        create_project_module.download_template(project_path, "wrongprotocol", True)
    assert not os.path.isdir(project_path)
