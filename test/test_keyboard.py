import pytest

from kf_lib.ui import _keyboard


def test_ctrl_c_raises_keyboard_interrupt(monkeypatch):
    monkeypatch.setattr(_keyboard, '_getch', lambda: '\x03')
    with pytest.raises(KeyboardInterrupt):
        _keyboard.getch()


def test_normal_key_passthrough(monkeypatch):
    monkeypatch.setattr(_keyboard, '_getch', lambda: 'a')
    assert _keyboard.getch() == 'a'
