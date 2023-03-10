"""
_tk_term_colors.py
10. March 2023

conversion from terminal to tkinter texbox colors

Author:
Nilusink
"""

SIMPLE_COLORS = [
    ('Black', 30, 0),  # BLack
    ("#75020c", 31, 0),  # Red
    ("#0f6903", 32, 0),  # Green
    ("#b39f07", 33, 0),  # Yellow
    ("#0f6bd4", 34, 0),  # Blue
    ("#ff00ff", 35, 0),  # Magenta
    ("#0eaba3", 36, 0),  # Cyan
    ("White", 37, 0),  # White
    ("Reset", 0, 0),  # Reset
]

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
    """
    print("called: ", color, control_code)
    if color == 0:
        return "reset"

    if control_code == 0:
        for col in SIMPLE_COLORS:
            if col[1] == color:
                return col[0]

        return "undefined"

    elif control_code == 1:
        return "unsuported"
        # for col in SIMPLE_COLORS:
        #     if col[1] == color:
        #         return color[0]
        #
        # return "undefined"

    return "undefined"
