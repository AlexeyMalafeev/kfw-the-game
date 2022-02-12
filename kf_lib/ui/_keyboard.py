from kf_lib.ui import getch


def get_key():
    """
    If key is pressed, return its string; if no key is pressed, return 0
    """
    # DEBUG MODE
    # return input('key:')
    # NORMAL MODE
    return chr(ord(getch()))
