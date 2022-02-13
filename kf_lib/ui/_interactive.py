from kf_lib.ui import get_key


def get_int_from_user(message, min_, max_) -> int:
    """
    Return an integer in range [a, b] (both included) input by user.
    """
    error_msg = 'invalid input, try again'
    while True:
        print(message)
        inp = input(f' ({min_}-{max_})>')
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
        print(message)
        inp = input(f' > ')
        if not inp and not can_be_empty:
            print(error_msg)
        else:
            return inp


def msg(message):
    print(message)
    pak()


def pak(silent=True):
    """
    Press any key.
    Wait for user to press any key.
    """
    if not silent:
        print('(Press any key)')
    get_key()


def pe():
    input('Press Enter')