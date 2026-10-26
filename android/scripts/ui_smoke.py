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
    device.enter("1")
    device.choose("no")
    device.choose("yes")
    device.choose("no")
    device.choose("yes")
    device.choose("Man")
    device.choose("yes")
    device.choose_first()
    device.save_and_quit()
    device.capture("saved-title")

    device.click_id("continue_game")
    move_menus = device.play_fight()
    if not move_menus:
        raise AssertionError("No fight move menus were exercised")
    device.wait_main()
    device.capture("final-title")
    print(f"UI smoke passed; fight menus exercised: {move_menus}")


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
