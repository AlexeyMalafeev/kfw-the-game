import pytest

from kf_lib.ui import _frontend
from kf_lib.ui._menu import menu
from kf_lib.ui._screen import cls


@pytest.fixture(autouse=True)
def clean_frontend():
    yield
    _frontend.uninstall_frontend()


def test_menu_is_presented_to_frontend():
    presented = []
    _frontend.install_frontend(
        key_reader=lambda: "2",
        menu_handler=lambda keys, options, weak: presented.append(
            (keys, options, weak)
        ),
    )

    result = menu([("One", 1), ("Two", 2)])

    assert result == 2
    assert presented == [("12", ["One", "Two"], False)]


def test_weak_menu_can_be_dismissed_by_frontend():
    presented = []
    _frontend.install_frontend(
        key_reader=lambda: "\x1b",
        menu_handler=lambda keys, options, weak: presented.append(weak),
    )

    assert menu(["Only option"], weak=True) is None
    assert presented == [True]


def test_clear_frontend_replaces_terminal_command(monkeypatch):
    cleared = []
    system_calls = []
    monkeypatch.setattr("kf_lib.ui._screen.os.system", system_calls.append)
    _frontend.install_frontend(clear_handler=lambda: cleared.append(True))

    cls()
    assert cleared == [True]
    assert system_calls == []

    _frontend.uninstall_frontend()
    cls()
    assert system_calls == ["clear"]


def test_key_frontend_and_desktop_fallback(monkeypatch):
    monkeypatch.setattr("kf_lib.ui._keyboard._getch", lambda: "d")
    _frontend.install_frontend(key_reader=lambda: "m")

    assert _frontend.read_key(lambda: "fallback") == "m"
    assert __import__("kf_lib.ui", fromlist=["get_key"]).get_key() == "m"

    _frontend.uninstall_frontend()
    assert __import__("kf_lib.ui", fromlist=["get_key"]).get_key() == "d"
