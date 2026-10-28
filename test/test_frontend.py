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


class ConsumingFrontend:
    """Like GameHost: each key read consumes the presented menu."""

    def __init__(self, keys):
        self.keys = list(keys)
        self.pending = None
        self.menus_at_read = []

    def present(self, keys, options, weak):
        self.pending = keys

    def read_key(self):
        self.menus_at_read.append(self.pending)
        self.pending = None
        return self.keys.pop(0)

    def install(self):
        _frontend.install_frontend(key_reader=self.read_key, menu_handler=self.present)


def test_menu_is_presented_again_after_invalid_key():
    frontend = ConsumingFrontend(["z", "\n", "2"])
    frontend.install()

    assert menu([("One", 1), ("Two", 2)]) == 2
    assert frontend.menus_at_read == ["12", "12", "12"]


def test_state_menu_is_presented_again_after_invalid_key(monkeypatch):
    from types import SimpleNamespace

    from kf_lib.game._state_menu import StateMenu

    monkeypatch.setattr("kf_lib.game._state_menu.cls", lambda: None)
    game = StateMenu.__new__(StateMenu)
    game.current_player = SimpleNamespace(
        get_p_info_verbose=lambda: "info", is_master=False
    )
    game.play_indefinitely = False
    frontend = ConsumingFrontend(["z", "b"])
    frontend.install()

    game.state_menu()

    assert frontend.menus_at_read == ["iamtbSLQXD", "iamtbSLQXD"]


def test_show_skips_fixed_column_wrap_when_frontend_wraps(capsys):
    from kf_lib.actors.human_controlled_fighter import HumanControlledFighter

    long_text = " ".join(["word"] * 30)
    HumanControlledFighter.show(None, long_text)
    assert all(len(line) <= 60 for line in capsys.readouterr().out.splitlines())

    _frontend.install_frontend(wraps_lines=True)
    HumanControlledFighter.show(None, long_text)
    assert capsys.readouterr().out == long_text + "\n"
