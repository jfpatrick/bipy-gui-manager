import pytest
import bipy_gui_manager.utils.cli as cli


strings = []


def mock_print(string):
    global strings
    strings.append(string)


def mock_input(string):
    global strings
    strings.append(string)


@pytest.fixture
def catch_stdout(monkeypatch):
    global strings
    strings = []
    monkeypatch.setattr('builtins.print', mock_print)
    monkeypatch.setattr('builtins.input', mock_input)
    yield
    strings = []


def test_print_welcome(catch_stdout):
    cli.print_welcome()
    assert strings == [
        "_________________________________________________________________________\n",
        "  Welcome to BI's PyQt5 Project Setup Wizard!",
        "_________________________________________________________________________\n",
    ]


def test_draw_line(catch_stdout):
    cli.draw_line()
    assert strings == ["\n_________________________________________________________________________\n"]


def test_ask_input(catch_stdout):
    cli.ask_input("give me input")
    assert strings == ["\033[0;33m=>\033[0;m give me input  "]


def test_handle_failure(catch_stdout):
    cli.handle_failure("what shall I do then?")
    assert strings == ["\033[0;31m=> Error!\033[0;33m what shall I do then? \033[0;m"]


def test_positive_feedback_no_newline(catch_stdout):
    cli.positive_feedback("That's some good news!", newline=False)
    assert strings == ["\033[0;32m=>\033[0;m That's some good news!  "]


def test_positive_feedback_with_newline(catch_stdout):
    cli.positive_feedback("That's some good news!")
    assert strings == ["\033[0;32m=>\033[0;m That's some good news!\n"]


def test_list_subtask(catch_stdout):
    cli.list_subtask("A small thing was done")
    assert strings == ["    - A small thing was done"]


def test_give_hint(catch_stdout):
    cli.give_hint("You can also try this!")
    assert strings == ["    - Hint: You can also try this!"]


def test_negative_feedback(catch_stdout):
    cli.negative_feedback("This wasn't good")
    assert strings == ["\033[0;31m=> Error!\033[0;33m This wasn't good\033[0;m"]