import string

from kf_lib.ui import cls, get_key


def menu(
    opt_list,
    title='',
    keys='1234567890' + string.ascii_lowercase,
    new_line=True,
    weak=False,
    options_per_page=20,
):
    """
    Ask the user to choose one of the options from the option list.
    The option list is either a list of strings
    (then return the selected option string on user choice),
    or a list of tuples (string, object),
    (then return the object matching the choice).
    """
    if isinstance(opt_list[0], tuple) and len(opt_list[0]) == 2:
        options = []
        returnables = []
        for a, b in opt_list:
            options.append(a)
            returnables.append(b)
    else:
        options = returnables = opt_list
    i = 0
    has_pages = False
    while True:
        curr_options = options[i: i + options_per_page]
        curr_returnables = returnables[i: i + options_per_page]
        curr_keys = keys[: len(curr_options)]
        if len(opt_list) > options_per_page:
            curr_options += ['Previous page', 'Next page']
            curr_keys += '<>'
            has_pages = True
        if title:
            print(title)
        if new_line:
            st = '\n'
        else:
            st = '; '
        print(st.join([f' {curr_keys[j]} - {curr_options[j]}' for j in range(len(curr_keys))]))
        while True:
            choice = get_key()
            if has_pages and choice in '<>':
                cls()
                if choice == '<':
                    i = max(0, i - options_per_page)
                elif options[i + options_per_page:]:
                    i += options_per_page
                break
            elif choice in curr_keys:
                return curr_returnables[curr_keys.index(choice)]
            elif weak:
                return


def yn(message):
    return menu((('yes', True), ('no', False)), message)
