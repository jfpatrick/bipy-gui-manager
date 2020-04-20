import os
import pytest
from argparse import Namespace
import bipy_gui_manager.create_project as create_project_module

from .conftest import create_template_files


def create_project_parameters(demo=True, force_demo=True, name=None, desc=None, author=None, email=None, repo=None,
                              clone_protocol="https", gitlab=True, template_path=None):
    args = Namespace(
        demo=demo,
        force_demo=force_demo,
        project_name=name,
        project_desc=desc,
        project_author=author,
        author_email=email,
        gitlab_repo=repo,
        clone_protocol=clone_protocol,
        gitlab=gitlab,
        template_path=template_path
    )
    return args


def test_most_common_right_values(mock_all_subtasks):
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    create_project_module.create_project(parameters)


def test_name_valid(mock_all_subtasks):
    # Right values
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    create_project_module.create_project(parameters)


def test_name_no_underscores(mock_all_subtasks):
    # Underscores not allowed
    parameters = create_project_parameters(name="test_project", desc="A test project", author="Me",
                                               email="m@cern.ch", repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ValueError):
        create_project_module.create_project(parameters)


def test_name_no_whitespace(mock_all_subtasks):
    # Whitespace not allowed
    parameters = create_project_parameters(name="test project", desc="A test project", author="Me",
                                           email="m@cern.ch", repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ValueError):
        create_project_module.create_project(parameters)


def test_name_no_not_alphanumeric(mock_all_subtasks):
    # Non-alphanumeric not allowed
    parameters = create_project_parameters(name="te$t(project)", desc="A test project", author="Me",
                                           email="m@cern.ch", repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ValueError):
        create_project_module.create_project(parameters)


def test_name_no_uppercase(mock_all_subtasks):
    # Uppercase not allowed
    parameters = create_project_parameters(name="TestProject", desc="A test project", author="Me",
                                           email="m@cern.ch", repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ValueError):
        create_project_module.create_project(parameters)


def test_name_no_empty_string(monkeypatch, mock_all_subtasks):
    # Empty string not allowed - will treat as None and ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(name="", desc="A test project", author="Me",
                                           email="m@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ZeroDivisionError):
        create_project_module.create_project(parameters)


def test_name_not_given(monkeypatch, mock_all_subtasks):
    # If not given as parameter will ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(desc="A test project", author="Me",
                                           email="m@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ZeroDivisionError):
        create_project_module.create_project(parameters)


def test_desc_valid(mock_all_subtasks):
    # Right values
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    create_project_module.create_project(parameters)


def test_desc_no_double_quotes(mock_all_subtasks):
    # Double quotes not allowed
    parameters = create_project_parameters(name="test-project", desc="A \"test\" project", author="Me",
                                           email="m@cern.ch", repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ValueError):
        create_project_module.create_project(parameters)


def test_desc_no_empty_string(monkeypatch, mock_all_subtasks):
    # Empty string not allowed - will treat as None and ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(name="test-project", desc="", author="Me",
                                           email="m@cern.ch", repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ZeroDivisionError):
        create_project_module.create_project(parameters)


def test_desc_not_given(monkeypatch, mock_all_subtasks):
    # If not given as parameter will ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(name="test-project", author="Me", email="m@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ZeroDivisionError):
        create_project_module.create_project(parameters)


def test_author_valid(mock_all_subtasks):
    # Right values
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    create_project_module.create_project(parameters)


def test_author_no_double_quotes(mock_all_subtasks):
    # Duoble quotes not allowed
    parameters = create_project_parameters(name="test-project", desc="A test project", author="M\"e",
                                           email="m@cern.ch", repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ValueError):
        create_project_module.create_project(parameters)


def test_author_no_empty_string(monkeypatch, mock_all_subtasks):
    # Empty string not allowed - will treat as None and ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="",
                                           email="m@cern.ch", repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ZeroDivisionError):
        create_project_module.create_project(parameters)


def test_author_not_given(monkeypatch, mock_all_subtasks):
    # If not given as parameter will ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(name="test-project", desc="A test project", email="m@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ZeroDivisionError):
        create_project_module.create_project(parameters)


def test_email_valid(mock_all_subtasks):
    # Right value
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    create_project_module.create_project(parameters)


def test_email_cern_domain_required(mock_all_subtasks):
    # Domain name must be CERN domain
    parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="me@email.com",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ValueError):
        create_project_module.create_project(parameters)


def test_email_local_part_is_required(monkeypatch, mock_all_subtasks):
    # Local part must be present
    parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ValueError):
        create_project_module.create_project(parameters)


def test_email_local_part_is_valid(monkeypatch, mock_all_subtasks):
    # Local part cannot contain any special char
    parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="m^)df@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ValueError):
        create_project_module.create_project(parameters)


def test_email_no_empty_string(monkeypatch, mock_all_subtasks):
    # Empty string not allowed - will treat as None and ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="", repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ZeroDivisionError):
        create_project_module.create_project(parameters)


def test_email_not_given(monkeypatch, mock_all_subtasks):
    # If not given as parameter will ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ZeroDivisionError):
        create_project_module.create_project(parameters)


def test_repo_https(mock_all_subtasks):
    # Right value
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="https://gitlab.cern.ch/user/project.git")
    create_project_module.create_project(parameters)
    # Nested
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="https://gitlab.cern.ch/group/subgroup/project.git")
    create_project_module.create_project(parameters)
    # Too short
    parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="me@cern.ch",
                                           repo="https://gitlab.cern.ch/project.git")
    with pytest.raises(ValueError):
        create_project_module.create_project(parameters)


def test_repo_ssh(mock_all_subtasks):
    # Right value
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    create_project_module.create_project(parameters)
    # Nested more than 2
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/group/subgroup/project.git")
    create_project_module.create_project(parameters)
    # Too short
    parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/project.git")
    with pytest.raises(ValueError):
        create_project_module.create_project(parameters)


def test_repo_krb5(mock_all_subtasks):
    # Right value
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="https://:@gitlab.cern.ch:8443/user/project.git")
    create_project_module.create_project(parameters)
    # Nested more than 2
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="https://:@gitlab.cern.ch:8443/group/subgroup/project.git")
    create_project_module.create_project(parameters)
    # Too short
    parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="me@cern.ch",
                                           repo="https://:@gitlab.cern.ch:8443/project.git")
    with pytest.raises(ValueError):
        create_project_module.create_project(parameters)


def test_repo_no_gitlab_interactive(mock_all_subtasks, monkeypatch):
    # Replying 'no-gitlab' in the CLI is allowed
    monkeypatch.setattr('builtins.input', lambda _: 'no-gitlab')
    parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="me@cern.ch")
    create_project_module.create_project(parameters)


def test_repo_no_garbage_address(mock_all_subtasks):
    parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="me@cern.ch",
                                           repo="https://gitlab.cern.ch.git")
    with pytest.raises(ValueError):
        create_project_module.create_project(parameters)


def test_repo_no_empty_string(monkeypatch, mock_all_subtasks):
    # Empty string not allowed - will treat as None and ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", repo="")
    with pytest.raises(ZeroDivisionError):
        create_project_module.create_project(parameters)


def test_repo_not_given(monkeypatch, mock_all_subtasks):
    # If not given as parameter will ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch")
    with pytest.raises(ZeroDivisionError):
        create_project_module.create_project(parameters)


def test_repo_not_checked_if_gitlab_false(mock_all_subtasks):
    # If gitlab=False, repo is not needed
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", gitlab=False)
    create_project_module.create_project(parameters)
    # If gitlab=False, repo is not checked
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", repo="T0t@l_g@rbage!!&$", gitlab=False)
    create_project_module.create_project(parameters)


def test_no_demo_flag_passed(monkeypatch, mock_all_subtasks):
    # If --no-demo is passed, the user is not asked anything and validate_demo_flags returns False
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", gitlab=False, force_demo=False, demo=False)
    create_project_module.create_project(parameters)
    assert not create_project_module.validate_demo_flags(force_demo=False, demo=False)


def test_with_demo_flag_passed(monkeypatch, mock_all_subtasks):
    # If --with-demo is passed, the user is not asked anything and validate_demo_flags returns True
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", gitlab=False, force_demo=True, demo=True)
    create_project_module.create_project(parameters)
    assert create_project_module.validate_demo_flags(force_demo=True, demo=True)


def test_demo_neither_flag_passed(monkeypatch, mock_all_subtasks):
    # If no flag is passed, the user is asked what to do
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", gitlab=False, force_demo=False, demo=True)
    with pytest.raises(ZeroDivisionError):
        create_project_module.create_project(parameters)
    with pytest.raises(ZeroDivisionError):
        create_project_module.validate_demo_flags(force_demo=False, demo=True)


def test_check_path_is_available_no_dir(tmpdir):
    project_path = os.path.join(tmpdir, "test_project")
    create_project_module.check_path_is_available(project_path)
    assert not os.path.exists(project_path)


def test_check_path_is_available_ask(tmpdir, monkeypatch):
    # Will ask whether to overwrite or not
    project_path = os.path.join(tmpdir, "test_project")
    os.mkdir(project_path)
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    with pytest.raises(ZeroDivisionError):
        create_project_module.check_path_is_available(project_path)


def test_check_path_is_available_say_no(tmpdir, monkeypatch):
    project_path = os.path.join(tmpdir, "test_project")
    os.mkdir(project_path)
    with open(os.path.join(project_path, "test_file"), "w") as testfile:
        testfile.write("Something")
    monkeypatch.setattr('builtins.input', lambda _: "no")
    # if is being said no, leave folder intact and exit with OSError
    with pytest.raises(OSError):
        create_project_module.check_path_is_available(project_path)
    assert os.path.isdir(project_path)
    assert not os.path.exists(os.path.join(project_path, "be_bi_pyqt_template"))
    assert os.path.exists(os.path.join(project_path, "test_file"))
    with open(os.path.join(project_path, "test_file"), "r") as testfile:
        assert testfile.read() == "Something"


def test_check_path_is_available_say_yes(tmpdir, monkeypatch):
    project_path = os.path.join(tmpdir, "test_project")
    os.mkdir(project_path)
    monkeypatch.setattr('builtins.input', lambda _: "yes")
    # if is being said yes, remove folder
    create_project_module.check_path_is_available(project_path)
    assert not os.path.isdir(project_path)


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
            "test-email@cern.ch\n",
            "Test author\n",
            "https://gitlab.cern.ch/test-project.git\n",
            "Something that does not change"
        ]


def test_git_init_and_push(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "test-project")
    create_template_files(project_path, "test-project", True)
    create_project_module.init_local_repo(project_path)
    create_project_module.push_first_commit(project_path, "https://gitlab.cern.ch/test-project.git")
