import os


def cls():
    from ._frontend import clear_screen

    clear_screen(lambda: os.system("cls" if os.name == "nt" else "clear"))
