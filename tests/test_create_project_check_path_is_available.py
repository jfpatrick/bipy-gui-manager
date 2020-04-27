import os
import pytest
import bipy_gui_manager.create_project.create_project as create_project_module


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


def test_check_path_is_available_not_interactive_passed(tmpdir, monkeypatch):
    project_path = os.path.join(tmpdir, "test_project")
    os.mkdir(project_path)
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    # Should not ask, directly fail
    with pytest.raises(OSError):
        create_project_module.check_path_is_available(project_path, interactive=False)
    assert os.path.isdir(project_path)


def test_check_path_is_available_overwrite_passed(tmpdir, monkeypatch):
    project_path = os.path.join(tmpdir, "test_project")
    os.mkdir(project_path)
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    # Should not ask, directly overwrite
    create_project_module.check_path_is_available(project_path, overwrite=True)
    assert not os.path.isdir(project_path)
