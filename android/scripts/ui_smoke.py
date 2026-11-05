#!/usr/bin/env python3
import argparse
import re
import subprocess
import time
import xml.etree.ElementTree as ET
from pathlib import Path

PACKAGE = "com.alexeymalafeev.kfw"
ACTIVITY = f"{PACKAGE}/.MainActivity"


class Device:
    def __init__(self, adb, artifacts):
        self.adb = adb
        self.artifacts = artifacts
        self.artifacts.mkdir(parents=True, exist_ok=True)

    def command(self, *args, binary=False):
        result = subprocess.run(
            [self.adb, *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result.stdout if binary else result.stdout.decode("utf-8", "replace")

    def shell(self, *args):
        return self.command("shell", *args)

    def nodes(self):
        self.shell("uiautomator", "dump", "/sdcard/kfw-ui-smoke.xml")
        xml = self.command("exec-out", "cat", "/sdcard/kfw-ui-smoke.xml")
        start = xml.find("<?xml")
        if start < 0:
            raise RuntimeError(f"Could not read UI hierarchy: {xml[:200]}")
        return ET.fromstring(xml[start:]).iter("node")

    @staticmethod
    def bounds(node):
        match = re.fullmatch(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", node.get("bounds", ""))
        if not match:
            return None
        x1, y1, x2, y2 = (int(value) for value in match.groups())
        return x1, y1, x2, y2

    @staticmethod
    def center(node):
        x1, y1, x2, y2 = Device.bounds(node)
        return (x1 + x2) // 2, (y1 + y2) // 2

    @staticmethod
    def inside(node, container):
        x, y = Device.center(node)
        x1, y1, x2, y2 = container
        return x1 <= x < x2 and y1 <= y < y2

    def find(self, nodes, resource_id=None, desc=None, text=None, prefix=False):
        result = []
        for node in nodes:
            if resource_id and not node.get("resource-id", "").endswith(
                f":id/{resource_id}"
            ):
                continue
            if desc is not None:
                value = node.get("content-desc", "")
                if prefix and not value.startswith(desc):
                    continue
                if not prefix and value != desc:
                    continue
            if text is not None:
                value = node.get("text", "")
                if prefix and not value.startswith(text):
                    continue
                if not prefix and value != text:
                    continue
            result.append(node)
        return result

    def visible_choice(self, node, nodes):
        if node.get("clickable") != "true" or node.get("enabled") != "true":
            return False
        scrolls = self.find(nodes, resource_id="input_scroll")
        if scrolls and self.bounds(scrolls[0]):
            return self.inside(node, self.bounds(scrolls[0]))
        return True

    def wait(self, resource_id=None, desc=None, text=None, prefix=False, timeout=60):
        deadline = time.monotonic() + timeout
        last_error = None
        while time.monotonic() < deadline:
            try:
                nodes = list(self.nodes())
                self.check_error(nodes)
                for node in self.find(nodes, resource_id, desc, text, prefix):
                    if self.visible_choice(node, nodes):
                        return node
            except (ET.ParseError, subprocess.CalledProcessError) as error:
                last_error = error
            time.sleep(0.4)
        raise TimeoutError(
            f"View not found: id={resource_id}, desc={desc}, text={text}, "
            f"prefix={prefix}; last error={last_error}"
        )

    def click(self, node):
        x, y = self.center(node)
        self.shell("input", "tap", str(x), str(y))
        time.sleep(0.2)

    def click_id(self, resource_id, timeout=60):
        self.click(self.wait(resource_id=resource_id, timeout=timeout))

    def scroll_choices(self, nodes, upwards=True):
        scroll = self.find(nodes, resource_id="input_scroll")[0]
        x1, y1, x2, y2 = self.bounds(scroll)
        x = (x1 + x2) // 2
        if upwards:
            start, end = y2 - 80, y1 + 80
        else:
            start, end = y1 + 80, y2 - 80
        self.shell("input", "swipe", str(x), str(start), str(x), str(end), "250")

    def choose(self, label, prefix=False, timeout=60):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            nodes = list(self.nodes())
            self.check_error(nodes)
            choices = self.find(nodes, desc=label, prefix=prefix)
            for choice in choices:
                if self.visible_choice(choice, nodes):
                    print(f"Choose: {label}", flush=True)
                    self.click(choice)
                    return
            if choices or self.find(nodes, resource_id="input_scroll"):
                self.scroll_choices(nodes)
            time.sleep(0.35)
        raise TimeoutError(f"Choice not found: {label!r}, prefix={prefix}")

    def choose_first(self):
        node = self.wait(text="1. ", prefix=True)
        self.click(node)

    def enter(self, text):
        field = self.wait(resource_id="line_input")
        self.click(field)
        if text:
            escaped = text.replace(" ", "%s").replace("&", "\\&")
            self.shell("input", "text", escaped)
        self.click_id("send_button")

    def wait_text(self, text, prefix=False, timeout=60):
        """Any view showing `text`, clickable or not (dialog items and messages)."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            nodes = list(self.nodes())
            self.check_error(nodes)
            found = self.find(nodes, text=text, prefix=prefix)
            if found:
                return found[0]
            time.sleep(0.4)
        raise TimeoutError(f"Text not found: {text!r}, prefix={prefix}")

    def tap_text(self, text, prefix=False, timeout=60):
        node = self.wait_text(text, prefix, timeout)
        print(f"Tap: {text}", flush=True)
        self.click(node)

    def play_ring(self):
        """A whole RING run on extreme, auto-fought, until it returns to the title."""
        self.click_id("minigames")
        self.tap_text("RING", prefix=True)
        self.click_id("continue_button")
        self.choose("extreme")
        self.enter("Smoke Tester")
        self.choose_first()
        self.enter("1")
        fights = 0
        for _ in range(400):
            nodes = list(self.nodes())
            self.check_error(nodes)
            if self.find(nodes, resource_id="new_game"):
                return fights
            if self.find(nodes, resource_id="line_input"):
                raise AssertionError("RING asked for text after character creation")
            if self.find(nodes, resource_id="continue_button"):
                self.click_id("continue_button")
                continue
            yes = [
                n for n in self.find(nodes, desc="yes") if self.visible_choice(n, nodes)
            ]
            if yes:
                self.choose("yes")  # Auto fight? (RING's only yes/no question)
                continue
            if self.find(nodes, desc="Stats") or self.find(nodes, desc="Timeline"):
                fights += 1
                if fights == 1:
                    self.capture("ring-after-fight")
                self.click_id("dismiss_menu")
                continue
            if self.find(nodes, resource_id="input_container"):
                choices = [
                    n for n in self.find(nodes, text="1. ", prefix=True)
                    if self.visible_choice(n, nodes)
                ]
                if choices:
                    self.click(choices[0])
                    continue
            time.sleep(0.35)
        raise TimeoutError("RING did not end in 400 input steps")

    def play_bag(self):
        """One Punching Bag round, first option everywhere, then back to the title."""
        self.click_id("minigames")
        self.tap_text("Punching Bag", prefix=True)
        self.click_id("continue_button")
        self.enter("Smoke Tester")
        self.choose_first()  # style; then the level-ups to level 10
        timed_menus = 0
        for _ in range(600):
            nodes = list(self.nodes())
            self.check_error(nodes)
            if self.find(nodes, resource_id="new_game"):
                return timed_menus
            if self.find(nodes, resource_id="continue_button"):
                self.click_id("continue_button")
                continue
            no = [
                n for n in self.find(nodes, desc="no") if self.visible_choice(n, nodes)
            ]
            if no:
                self.capture("bag-score")
                self.choose("no")  # Another round?
                continue
            if self.find(nodes, desc="Stats") or self.find(nodes, desc="Timeline"):
                self.click_id("dismiss_menu")
                continue
            if self.find(nodes, resource_id="input_container"):
                console = self.find(nodes, resource_id="console")
                text = console[0].get("text", "") if console else ""
                choices = [
                    n for n in self.find(nodes, text="1. ", prefix=True)
                    if self.visible_choice(n, nodes)
                ]
                if choices:
                    if "time left" in text[-400:]:
                        timed_menus += 1
                        if timed_menus == 3:
                            self.capture("bag-round")
                    self.click(choices[0])
                    continue
            time.sleep(0.35)
        raise TimeoutError("The Punching Bag did not end in 600 input steps")

    def leave_chocolate(self):
        """Start Chocolate, then leave it from the toolbar's title button."""
        self.click_id("minigames")
        self.tap_text("Chocolate", prefix=True)
        self.click_id("continue_button")  # the welcome screen
        self.wait(resource_id="continue_button")  # scene 1 teaches its techniques
        self.capture("chocolate-scene-1")
        # a toolbar button, outside the answer panel that wait() looks in
        self.click(self.find(list(self.nodes()), resource_id="home_button")[0])
        # the mini-game warning, not the main game's "since your last save" one
        self.wait_text("Return to the title screen? This mini-game", prefix=True)
        self.capture("chocolate-leave")
        # the positive button ("Leave without saving"; themes may capitalize it)
        self.click(self.find(list(self.nodes()), resource_id="button1")[0])
        self.wait_main()

    def check_error(self, nodes):
        errors = self.find(nodes, text="The game stopped unexpectedly")
        if errors:
            console = self.find(nodes, resource_id="console")
            details = console[0].get("text", "")[-2000:] if console else ""
            raise AssertionError(f"Android game error dialog. Console: {details}")

    def capture(self, name):
        path = self.artifacts / f"{name}.png"
        data = self.command("exec-out", "screencap", "-p", binary=True)
        path.write_bytes(data)

    def wait_main(self):
        self.wait(resource_id="new_game")

    def save_and_quit(self):
        self.choose("State")
        self.choose("Save")
        self.choose("Save and Quit")
        self.wait_main()

    def practice(self):
        """State > Moves > Punching Bag, 10 moves, then back to the day."""
        self.choose("State")
        self.choose("Moves")
        self.choose("Punching Bag")
        self.choose("10 moves")
        moves = 0
        for _ in range(200):
            nodes = list(self.nodes())
            self.check_error(nodes)
            # back in the State menu (it opens at its first options)
            if self.find(nodes, desc="Save and Quit") or (
                self.find(nodes, desc="Items")
                and self.find(nodes, desc="Accomplishments")
            ):
                self.choose("Back")
                return moves
            if self.find(nodes, resource_id="continue_button"):
                self.click_id("continue_button")
                continue
            if self.find(nodes, desc="Stats") or self.find(nodes, desc="Timeline"):
                self.capture("practice-summary")
                self.click_id("dismiss_menu")
                continue
            if self.find(nodes, resource_id="input_container"):
                console = self.find(nodes, resource_id="console")
                text = console[0].get("text", "") if console else ""
                choices = [
                    n for n in self.find(nodes, text="1. ", prefix=True)
                    if self.visible_choice(n, nodes)
                ]
                if choices:
                    if "moves left" in text[-400:]:
                        moves += 1
                        if moves == 3:
                            self.capture("practice")
                    self.click(choices[0])
                    continue
            time.sleep(0.35)
        raise TimeoutError("The practice did not end in 200 input steps")

    def play_fight(self):
        self.choose("State")
        self.choose("Debug Menu")
        self.choose("Fight Thug(s)")
        self.enter("1")
        move_menus = 0
        postfight = False
        captured = False
        for _ in range(300):
            nodes = list(self.nodes())
            self.check_error(nodes)
            if self.find(nodes, resource_id="new_game"):
                raise AssertionError("Returned to title before the fight finished")
            if self.find(nodes, resource_id="line_input"):
                self.enter("")
                continue
            if self.find(nodes, resource_id="continue_button"):
                self.click_id("continue_button")
                continue
            yes = [
                n for n in self.find(nodes, desc="yes") if self.visible_choice(n, nodes)
            ]
            no = [
                n for n in self.find(nodes, desc="no") if self.visible_choice(n, nodes)
            ]
            if yes and no:
                console = self.find(nodes, resource_id="console")
                text = console[0].get("text", "") if console else ""
                if "Auto fight?" in text:
                    if postfight:
                        print("Choosing automatic follow-up combat", flush=True)
                        self.click(yes[0])
                    else:
                        print("Choosing manual combat", flush=True)
                        self.click(no[0])
                    continue
            state_menu = self.find(nodes, desc="Save and Quit") or (
                self.find(nodes, desc="Items")
                and self.find(nodes, desc="Accomplishments")
            )
            if state_menu and postfight:
                self.capture("after-fight")
                self.choose("Save and Quit")
                self.wait_main()
                return move_menus
            if self.find(nodes, desc="State") and postfight:
                self.capture("after-fight")
                self.save_and_quit()
                return move_menus
            postfight_menu = self.find(nodes, desc="Stats") or self.find(
                nodes, desc="Timeline"
            )
            back = [
                n
                for n in self.find(nodes, desc="Back")
                if self.visible_choice(n, nodes)
            ]
            back += [
                n
                for n in self.find(nodes, text="Back")
                if self.visible_choice(n, nodes)
            ]
            if back and postfight_menu:
                postfight = True
                print("Post-fight Back", flush=True)
                self.click(back[0])
                continue
            fight = [
                n
                for n in self.find(nodes, desc="Fight!", prefix=True)
                if self.visible_choice(n, nodes)
            ]
            if fight:
                print("Accepting a fight", flush=True)
                self.click(fight[0])
                continue
            choices = []
            container = self.find(nodes, resource_id="input_container")
            if container:
                scroll_bounds = self.bounds(
                    self.find(nodes, resource_id="input_scroll")[0]
                )
                for node in nodes:
                    if (
                        node.get("class") == "android.widget.Button"
                        and node.get("clickable") == "true"
                        and self.inside(node, scroll_bounds)
                    ):
                        choices.append(node)
            if choices:
                console = self.find(nodes, resource_id="console")
                text = console[0].get("text", "") if console else ""
                print(
                    "Menu:",
                    [node.get("content-desc", "") for node in choices[:3]],
                    "console:",
                    repr(text[:160]),
                    flush=True,
                )
                if "HP " in text and "SP " in text:
                    move_menus += 1
                    if not captured:
                        self.capture("fight")
                        captured = True
                self.click(choices[0])
                continue
            time.sleep(0.35)
        raise TimeoutError("Fight did not finish in 300 input steps")


def run(args):
    device = Device(args.adb, args.artifacts)
    if args.reset:
        device.shell("pm", "clear", PACKAGE)
    device.shell("am", "force-stop", PACKAGE)
    device.shell("am", "start", "-W", "-n", ACTIVITY)
    device.wait_main()
    device.capture("title")

    device.click_id("new_game")
    # a key outside the menu must leave the menu buttons in place
    device.wait(desc="no")
    device.shell("input", "keyevent", "KEYCODE_Z")
    time.sleep(0.8)
    device.choose("no")
    device.shell("input", "keyevent", "KEYCODE_HOME")
    time.sleep(0.8)
    device.shell("am", "start", "-W", "-n", ACTIVITY)
    device.wait(resource_id="line_input")
    device.shell("settings", "put", "system", "user_rotation", "1")
    time.sleep(0.8)
    device.wait(resource_id="line_input")
    device.shell("settings", "put", "system", "user_rotation", "0")
    time.sleep(0.8)
    # a system font-size change must not drop the running game to the title
    font_scale = device.shell("settings", "get", "system", "font_scale").strip()
    if font_scale in ("", "null"):
        font_scale = "1.0"
    device.shell("settings", "put", "system", "font_scale", "1.15")
    time.sleep(0.8)
    try:
        device.wait(resource_id="line_input", timeout=10)
    finally:
        device.shell("settings", "put", "system", "font_scale", font_scale)
        time.sleep(0.8)
    device.wait(resource_id="line_input")
    device.enter("1")
    device.choose("no")
    device.choose("yes")
    device.choose("no")
    device.choose("yes")
    device.choose("Man")
    device.choose("yes")
    device.choose_first()
    # the exact move count is pinned by test/test_punching_bag.py
    if not device.practice():
        raise AssertionError("The practice showed no move menu")
    device.save_and_quit()
    device.capture("saved-title")

    device.click_id("continue_game")
    move_menus = device.play_fight()
    if not move_menus:
        raise AssertionError("No fight move menus were exercised")
    device.wait_main()
    device.capture("final-title")

    ring_fights = device.play_ring()
    if not ring_fights:
        raise AssertionError("RING ended without a fight")
    bag_moves = device.play_bag()
    if not bag_moves:
        raise AssertionError("The Punching Bag round showed no timed move menu")
    device.leave_chocolate()
    print(
        f"UI smoke passed; fight menus exercised: {move_menus}; "
        f"RING fights: {ring_fights}; Punching Bag moves: {bag_moves}"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Drive the real KFW Android UI through adb"
    )
    parser.add_argument("--adb", default="adb")
    parser.add_argument(
        "--reset", action="store_true", help="Clear app data before the test"
    )
    parser.add_argument(
        "--artifacts", type=Path, default=Path("android/build/ui-smoke")
    )
    run(parser.parse_args())


if __name__ == "__main__":
    main()
