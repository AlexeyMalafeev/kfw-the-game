try:
    import msvcrt

    def getch():
        return msvcrt.getch().decode('ascii', errors='replace')
except ImportError:
    import sys
    import termios
    import tty

    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


def get_key():
    """
    If key is pressed, return its string; if no key is pressed, return 0
    """
    # DEBUG MODE
    # return input('key:')
    # NORMAL MODE
    return getch()
