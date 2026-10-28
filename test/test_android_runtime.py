import builtins
import json
import os
import random
import sys
from pathlib import Path

from android.python import kfw_android

REPO_ROOT = Path(__file__).resolve().parent.parent


class FakeHost:
    def __init__(self, loaded=False):
        self.loaded = loaded
        self.pending = None
        self.output = []
        self.finished_states = []
        self.saved = False
        self.line_answers = ["1"]
        self.tunes = []

    def playMusic(self, tune):
        self.tunes.append(tune)

    def playSound(self, effect):
        pass

    def isClosed(self):
        return False

    def write(self, text):
        self.output.append(text)

    def clear(self):
        self.output.append("\n--- clear ---\n")

    def presentMenu(self, keys, labels, weak):
        self.pending = (keys, json.loads(labels), weak)

    def readLine(self):
        if self.line_answers:
            return self.line_answers.pop(0)
        return ""

    def readKey(self):
        if self.pending is None:
            return " "
        keys, labels, weak = self.pending
        self.pending = None

        def choose(label):
            return keys[labels.index(label)]

        if "State" in labels:
            return choose("State")
        if "Save and Quit" in labels:
            if self.loaded:
                return choose("Quit")
            if self.saved:
                return choose("Save and Quit")
            self.saved = True
            return choose("Save")
        if "Man" in labels:
            return choose("Man")
        if labels == ["yes", "no"]:
            transcript = "".join(self.output)
            if "Auto save?" in transcript[-1000:]:
                return choose("yes")
            if "Is this character ok?" in transcript[-1000:]:
                return choose("yes")
            if "human player?" in transcript[-1000:]:
                return choose("yes")
            return choose("no")
        if weak:
            return "\x1b"
        return keys[0]

    def finished(self, status):
        self.finished_states.append(status)


def test_android_runtime_new_game_save_and_load(tmp_path):
    random.seed(0)
    home = tmp_path / "android-home"
    old_cwd = Path.cwd()
    old_stdout = sys.stdout
    old_input = builtins.input
    host = FakeHost()
    os.chdir(tmp_path)

    status = kfw_android.run(
        host,
        mode="new",
        language="en",
        home=home,
        resource_root=REPO_ROOT,
    )

    assert status == "finished"
    assert host.finished_states == ["finished"]
    # character creation, then the first town day
    assert host.tunes[:2] == ["02_choosing_a_style", "03_morning_market"]
    save_path = home / "save" / "save.txt"
    assert save_path.is_file()
    save_data = json.loads(save_path.read_text())
    assert save_data["format"] == "kfw-save"
    assert len(save_data["players"]) == 1
    assert (home / "moves" / "all_moves.txt").is_file()
    assert (home / "locale" / "ru" / "LC_MESSAGES" / "kfw.mo").is_file()
    assert Path.cwd() == tmp_path
    os.chdir(old_cwd)
    assert Path.cwd() == old_cwd
    assert sys.stdout is old_stdout
    assert builtins.input is old_input

    loaded_host = FakeHost(loaded=True)
    status = kfw_android.run(
        loaded_host,
        mode="load",
        language="en",
        save_name="save.txt",
        home=home,
        resource_root=REPO_ROOT,
    )

    assert status == "finished"
    assert loaded_host.finished_states == ["finished"]
    assert loaded_host.saved is False
    assert Path.cwd() == old_cwd
    assert sys.stdout is old_stdout
    assert builtins.input is old_input


def test_android_runtime_missing_resources_fail_cleanly(tmp_path):
    host = FakeHost()

    status = kfw_android.run(
        host,
        home=tmp_path / "home",
        resource_root=tmp_path / "missing",
    )

    assert status == "error"
    assert host.finished_states == ["error"]


def test_android_new_game_restores_style_defaults():
    from kf_lib.kung_fu import styles

    previous = list(styles.default_styles)
    previous_cache = kfw_android._DEFAULT_STYLES
    try:
        kfw_android._DEFAULT_STYLES = None
        kfw_android._reset_default_styles()
        styles.default_styles = [object()]
        kfw_android._reset_default_styles()
        assert styles.default_styles == previous
    finally:
        styles.default_styles = previous
        kfw_android._DEFAULT_STYLES = previous_cache
