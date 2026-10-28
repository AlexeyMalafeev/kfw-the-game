import builtins
import io
import json
import os
import pprint
import shutil
import sys
import time
import traceback
from pathlib import Path

RESOURCE_DIRS = ("moves", "quotes", "locale")


class SessionClosed(Exception):
    pass


def default_resource_root():
    here = Path(__file__).resolve().parent
    if all((here / name).is_dir() for name in RESOURCE_DIRS):
        return here
    return here.parent.parent


def prepare_home(home, resource_root=None):
    home = Path(home).resolve()
    resource_root = Path(resource_root or default_resource_root()).resolve()
    home.mkdir(parents=True, exist_ok=True)
    for name in RESOURCE_DIRS:
        source = resource_root / name
        if not source.is_dir():
            raise FileNotFoundError(f"Missing KFW resource directory: {source}")
        shutil.copytree(source, home / name, dirs_exist_ok=True)
    for name in ("save", "tests"):
        (home / name).mkdir(exist_ok=True)
    return home


class HostStream(io.TextIOBase):
    def __init__(self, runtime):
        self.runtime = runtime

    def write(self, text):
        text = str(text)
        if not text:
            return 0
        self.runtime.ensure_open()
        self.runtime.host.write(text)
        return len(text)

    def flush(self):
        return None

    def isatty(self):
        return True

    @property
    def encoding(self):
        return "utf-8"


class AndroidRuntime:
    def __init__(self, host):
        self.host = host
        self.closed = False
        self.stream = HostStream(self)
        self.old_state = None

    def ensure_open(self):
        if self.closed or self.host.isClosed():
            raise SessionClosed

    def install(self):
        if self.old_state is not None:
            raise RuntimeError("Android runtime is already installed")
        from kf_lib.ui import _frontend, _rich_format

        self.old_state = {
            "stdout": sys.stdout,
            "stderr": sys.stderr,
            "input": builtins.input,
            "cwd": Path.cwd(),
            "home": os.environ.get("HOME"),
            "colors": _rich_format.colors_enabled(),
        }
        sys.stdout = self.stream
        sys.stderr = self.stream
        builtins.input = self.read_line
        _frontend.install_frontend(
            key_reader=self.read_key,
            clear_handler=self.clear,
            menu_handler=self.present_menu,
            wraps_lines=True,
        )
        _rich_format.set_colors_enabled(True)

    def uninstall(self):
        if self.old_state is None:
            return
        from kf_lib.ui import _frontend, _rich_format

        _frontend.uninstall_frontend()
        sys.stdout = self.old_state["stdout"]
        sys.stderr = self.old_state["stderr"]
        builtins.input = self.old_state["input"]
        os.chdir(self.old_state["cwd"])
        if self.old_state["home"] is None:
            os.environ.pop("HOME", None)
        else:
            os.environ["HOME"] = self.old_state["home"]
        _rich_format.set_colors_enabled(self.old_state["colors"])
        self.old_state = None

    def __enter__(self):
        self.install()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.uninstall()

    def read_key(self):
        self.ensure_open()
        key = self.host.readKey()
        if key is None:
            raise SessionClosed
        return str(key)

    def read_line(self, prompt=""):
        self.ensure_open()
        if prompt:
            self.stream.write(str(prompt))
        line = self.host.readLine()
        if line is None:
            raise SessionClosed
        line = str(line)
        self.stream.write(line + "\n")
        return line

    def clear(self):
        self.ensure_open()
        self.host.clear()

    def present_menu(self, keys, options, weak=False):
        from kf_lib.ui import strip_tags

        self.ensure_open()
        labels = [strip_tags(str(option)) for option in options]
        self.host.presentMenu(
            "".join(keys), json.dumps(labels, ensure_ascii=False), bool(weak)
        )


_DEFAULT_STYLES = None


def _reset_default_styles():
    global _DEFAULT_STYLES
    from kf_lib.kung_fu import styles

    if _DEFAULT_STYLES is None:
        _DEFAULT_STYLES = list(styles.default_styles)
    else:
        styles.default_styles = list(_DEFAULT_STYLES)


def _new_game(game_module, player_module, ui, ai_only=False):
    from kf_lib.i18n import _

    _reset_default_styles()
    g = game_module.Game()
    if ai_only:
        g.new_game(
            num_players=4,
            coop=False,
            ai_only=True,
            auto_save_on=False,
            generated_styles=True,
            forced_aip_class=player_module.SmartAIPVisible,
            silent_ending=False,
        )
    else:
        visible_ai = ui.yn(_("Do you want to see what AI players do?"))
        default_ai = (
            player_module.SmartAIPVisible if visible_ai else player_module.SmartAIP
        )
        g.new_game(forced_aip_class=default_ai, confirm_styles_with_player=True)
    return g


def _write_crash_report(g):
    now = time.ctime()
    with open("errors.txt", "a", encoding="utf-8") as error_file:
        print(f"\n\n{now}\n", file=error_file)
        traceback.print_exc(file=error_file)
    with open("debug.txt", "a", encoding="utf-8") as debug_file:
        print(f"\n\n{now}\n", file=debug_file)
        if g is not None:
            pprint.pprint(vars(g), stream=debug_file)
    if g is not None:
        try:
            g.save_game("emergency_save.txt")
        except Exception:
            traceback.print_exc()


def run(host, mode="new", language="en", save_name=None, home=None, resource_root=None):
    runtime = AndroidRuntime(host)
    g = None
    status = "finished"
    old_cwd = Path.cwd()
    old_home = os.environ.get("HOME")
    try:
        home = prepare_home(
            home if home is not None else os.environ["HOME"], resource_root
        )
        os.chdir(home)
        os.environ["HOME"] = str(home)
        with runtime:
            from kf_lib import i18n

            i18n.set_language(language)
            from kf_lib import game as game_module
            from kf_lib import ui
            from kf_lib.actors import player as player_module

            try:
                if mode == "load":
                    if not save_name:
                        raise ValueError("A save file is required in load mode")
                    g = game_module.Game()
                    g.load_game(save_name)
                elif mode in ("new", "ai"):
                    g = _new_game(game_module, player_module, ui, ai_only=mode == "ai")
                else:
                    raise ValueError(f"Unknown Android game mode: {mode}")
                g.play()
            except SessionClosed:
                status = "stopped"
            except KeyboardInterrupt:
                status = "stopped"
            except Exception:
                status = "error"
                traceback.print_exc()
                try:
                    _write_crash_report(g)
                except Exception:
                    traceback.print_exc()
    except SessionClosed:
        status = "stopped"
    except Exception:
        status = "error"
        traceback.print_exc()
    finally:
        os.chdir(old_cwd)
        if old_home is None:
            os.environ.pop("HOME", None)
        else:
            os.environ["HOME"] = old_home
        try:
            host.finished(status)
        except Exception:
            pass
    return status
