import json
import os
import random
import re
import shutil
from pathlib import Path
from types import SimpleNamespace

import kfw_android


class ScriptedHost:
    def __init__(self, loaded=False):
        self.loaded = loaded
        self.pending = None
        self.output = []
        self.finished_states = []
        self.saved = False
        self.line_answers = ["1"]
        self.menu_count = 0

    def isClosed(self):
        return False

    def write(self, text):
        self.output.append(text)

    def clear(self):
        self.output.append("\n--- clear ---\n")

    def presentMenu(self, keys, labels, weak):
        self.pending = (keys, json.loads(labels), weak)
        self.menu_count += 1

    def readLine(self):
        return self.line_answers.pop(0) if self.line_answers else ""

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
            if any(
                text in transcript[-1000:]
                for text in ("Auto save?", "Is this character ok?", "human player?")
            ):
                return choose("yes")
            return choose("no")
        if weak:
            return "\x1b"
        return keys[0]

    def finished(self, status):
        self.finished_states.append(status)


def check_russian_resources(home):
    old_cwd = Path.cwd()
    old_home = os.environ.get("HOME")
    try:
        os.chdir(home)
        os.environ["HOME"] = str(home)
        from kf_lib import i18n

        i18n.set_language("ru")
        assert i18n._("Auto save?") == "Автосохранение?"
        assert i18n.tr_name("Tiger") == "Тигр"
        from kf_lib.actors import quotes

        assert len(quotes.WISDOM) > 10
        assert any("мастер" in quote.lower() for quote in quotes.WISDOM)
        i18n.set_language("en")
    finally:
        os.chdir(old_cwd)
        if old_home is None:
            os.environ.pop("HOME", None)
        else:
            os.environ["HOME"] = old_home


def check_save_and_load(home):
    host = ScriptedHost()
    status = kfw_android.run(
        host,
        mode="new",
        language="en",
        home=home,
        resource_root=kfw_android.default_resource_root(),
    )
    assert status == "finished", status
    save = home / "save" / "save.txt"
    assert save.is_file()
    data = json.loads(save.read_text(encoding="utf-8"))
    assert data["format"] == "kfw-save"
    assert len(data["players"]) == 1

    loaded = ScriptedHost(loaded=True)
    status = kfw_android.run(
        loaded,
        mode="load",
        language="en",
        save_name="save.txt",
        home=home,
        resource_root=kfw_android.default_resource_root(),
    )
    assert status == "finished", status
    return len(data["fighters"])


def check_interactive_fight(home):
    from kf_lib import game
    from kf_lib.actors.fighter_factory import new_fighter
    from kf_lib.actors.player import HumanPlayer
    from kf_lib.fighting.fight._normal_fight import NormalFight

    host = ScriptedHost()
    old_cwd = Path.cwd()
    old_home = os.environ.get("HOME")
    try:
        os.chdir(home)
        os.environ["HOME"] = str(home)
        with kfw_android.AndroidRuntime(host):
            player = HumanPlayer("Android Device Tester", "Tiger", 5)
            player.game = SimpleNamespace(fights_total=0, get_date=lambda: "1/1/1")
            opponent = new_fighter(1)
            fight = NormalFight([player], [opponent], items_allowed=False)
    finally:
        os.chdir(old_cwd)
        if old_home is None:
            os.environ.pop("HOME", None)
        else:
            os.environ["HOME"] = old_home
    assert fight.winners == [player]
    assert host.menu_count > 0
    transcript = re.sub(r"\x1b\[[0-9;]*m", "", "".join(host.output))
    assert "HP " in transcript
    return host.menu_count


def run_suite(files_directory):
    home = Path(files_directory) / "python-selftest-home"
    if home.exists():
        shutil.rmtree(home)
    home = kfw_android.prepare_home(home)
    random.seed(4)
    check_russian_resources(home)
    fighters = check_save_and_load(home)
    random.seed(4)
    fight_menus = check_interactive_fight(home)
    return json.dumps(
        {
            "status": "passed",
            "fighters": fighters,
            "fight_menus": fight_menus,
            "russian": True,
        }
    )


def main():
    return run_suite(os.environ["HOME"])
