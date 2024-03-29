"""
_tk_term_colors.py
10. March 2023

conversion from terminal to tkinter texbox colors

Author:
Nilusink
"""

SIMPLE_COLORS = {
    "black": ("Black", 30, 0),
    "red": ("#fc0307", 31, 0),
    "green": ("#0f6903", 32, 0),
    "yellow": ("#b39f07", 33, 0),
    "blue": ("#0f6bd4", 34, 0),
    "magenta": ("#ff00ff", 35, 0),
    "cyan": ("#0eaba3", 36, 0),
    "white": ("White", 37, 0),
    "reset": ("Reset", 0, 0),
}

COMPLEX_COLORS = [
    ("Bright Black", 30, 1),
    ("Bright Red", 31, 1),
    ("Bright Green", 32, 1),
    ("Bright Yellow", 33, 1),
    ("Bright Blue", 34, 1),
    ("Bright Magenta", 35, 1),
    ("Bright Cyan", 36, 1),
    ("Bright White", 37, 1),
]


def cmd_to_tk(color: int, control_code: int = 0) -> str:
    """
    convert a terminal color to a tkinter valid color
    """
    if color == 0:
        return "reset"

    if control_code == 0:
        for col in SIMPLE_COLORS.values():
            if col[1] == color:
                return col[0]

        return "undefined"

    elif control_code == 1:
        return "unsupported"

    return "undefined"


def read_color_code(stdout) -> str:
    """
    read the current color (only call after 27)

    :param stdout: stdout pipe
    :return:
    """
    curr = b""
    n_char = stdout.read(1)
    while n_char[0] != 109:
        curr += n_char
        n_char = stdout.read(1)

        if len(curr) > 10:
            raise ValueError

    control_code = 0
    s_curr = curr.decode().lstrip("[").rstrip("m")
    if ";" in s_curr:
        control_code, color = s_curr.split(";")

    else:
        color = s_curr

    tk_col = cmd_to_tk(int(color), int(control_code))
    if tk_col.lower() in ("reset", "undefined", "unsupported"):
        return ""

    return tk_col
