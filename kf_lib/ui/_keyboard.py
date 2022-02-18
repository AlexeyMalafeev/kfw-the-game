# try:
#     import msvcrt  # noqa
#
#     getch = msvcrt.getch
# except ImportError:
#     import sys
#     import tty
#     import termios
#
#     def getch():
#         fd = sys.stdin.fileno()
#         old_settings = termios.tcgetattr(fd)
#         try:
#             tty.setraw(sys.stdin.fileno())
#             ch = sys.stdin.read(1)
#         finally:
#             termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
#         return ch
import msvcrt


def get_key():
    """
    If key is pressed, return its string; if no key is pressed, return 0
    """
    # DEBUG MODE
    # return input('key:')
    # NORMAL MODE
    return chr(ord(msvcrt.getch()))
