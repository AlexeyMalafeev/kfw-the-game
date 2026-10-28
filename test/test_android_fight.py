import json
import os
import random
import re
from pathlib import Path
from types import SimpleNamespace

from android.python import kfw_android

REPO_ROOT = Path(__file__).resolve().parent.parent


class FightHost:
    def __init__(self):
        self.pending = None
        self.output = []
        self.menu_count = 0
        self.closed = False
        self.tunes = []
        self.effects = []

    def isClosed(self):
        return self.closed

    def write(self, text):
        self.output.append(text)

    def clear(self):
        pass

    def playMusic(self, tune):
        self.tunes.append(tune)

    def playSound(self, effect):
        self.effects.append(effect)

    def presentMenu(self, keys, labels, weak):
        self.pending = (keys, json.loads(labels), weak)
        self.menu_count += 1

    def readLine(self):
        return ""

    def readKey(self):
        if self.pending is None:
            return " "
        keys, labels, weak = self.pending
        self.pending = None
        if weak:
            return "\x1b"
        return keys[0]

    def finished(self, status):
        pass


def test_android_runtime_runs_interactive_fight_to_completion(tmp_path):
    from kf_lib import game
    from kf_lib import i18n
    from kf_lib.actors.fighter_factory import new_fighter
    from kf_lib.actors.player import HumanPlayer
    from kf_lib.fighting.fight._normal_fight import NormalFight

    random.seed(4)
    home = kfw_android.prepare_home(tmp_path / "home", REPO_ROOT)
    host = FightHost()
    old_cwd = Path.cwd()
    old_home = os.environ.get("HOME")
    try:
        with kfw_android.AndroidRuntime(host):
            os.chdir(home)
            os.environ["HOME"] = str(home)
            i18n.set_language("en")
            player = HumanPlayer("Android Tester", "Tiger", 5)
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
    assert fight.losers == [opponent]
    assert host.menu_count >= 1
    transcript = re.sub(r"\x1b\[[0-9;]*m", "", "".join(host.output))
    assert "HP " in transcript
    assert "wins" in transcript or "Android Tester" in transcript
    assert player.game.fights_total == 1
    # the fight plays its tune, effects and the victory jingle, then the music
    # goes back to what played before it (silence here)
    assert host.tunes[0] in ("08_fists_like_rain", "09_alley_cats", "10_thugs_at_the_bridge")
    assert host.tunes[1:] == [""]
    assert host.effects[0] == "fight_start"
    assert "victory" in host.effects
    for name in host.effects:
        assert (REPO_ROOT / "audio" / "sfx" / f"{name}.ogg").is_file(), name
