from ._keyboard import get_key
from ._rich_format import grey, render, rprint


def get_int_from_user(message, min_, max_, can_cancel=False):
    """
    Return an integer in range [a, b] (both included) input by user.
    If can_cancel is True, entering 'b' returns None (go back).
    """
    error_msg = 'invalid input, try again'
    cancel_hint = ", 'b' to go back" if can_cancel else ''
    while True:
        rprint(message)
        inp = input(f' ({min_}-{max_}{cancel_hint})> ')
        if can_cancel and inp.strip().lower() == 'b':
            return None
        try:
            inp = int(inp)
        except ValueError:
            print(error_msg)
            continue
        if min_ <= inp <= max_:
            return inp
        else:
            print(error_msg)


def get_str_from_user(message, can_be_empty=False) -> str:
    error_msg = 'invalid input, try again'
    while True:
        rprint(message)
        inp = input(f' > ')
        if not inp and not can_be_empty:
            print(error_msg)
        else:
            return inp


def msg(message):
    rprint(message)
    pak()


def pak(silent=True):
    """
    Press any key.
    Wait for user to press any key.
    """
    if not silent:
        print(render(grey('(Press any key)')))
    get_key()


def pe():
    input(render(grey('Press Enter')))
