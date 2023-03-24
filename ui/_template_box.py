"""
ui/_template_box.py

Project: BotballUI
Created: 24.03.2023
Author: Lukas Krahbichler
"""

##################################################
#                    Imports                     #
##################################################

from customtkinter import CTkFrame, CTkButton, CTkFont
from typing import Any, Optional, Union, Callable
from tkinter import Event, Misc


##################################################
#                     Code                       #
##################################################

class TemplateBox(CTkFrame):
    """
    Some buttons for termbox
    """
    __buttons: list[CTkButton]
    __callback: Callable[[str, Event], any]
    __font = Optional[Union[tuple, CTkFont]]
    KEYSYM: dict[str, str] = {
        "\r": "return",
        "\n": "return",
        "\x08": "backspace",
        " ": "space"
    }

    def __init__(
            self,
            master: Misc,
            buttons: dict[str, str],
            callback: Callable[[str, Event], any],
            *args: Any,
            font: Optional[Union[tuple, CTkFont]] = None,
            **kwargs: Any
    ) -> None:
        super().__init__(master, *args, **kwargs)
        self.configure(width=0, height=0)

        self.__buttons = []
        self.__callback = callback
        self.__font = font

        for but in buttons:
            self.__buttons.append(
                CTkButton(self, text=but, font=font, command=lambda k=buttons[but]: self.press(k))
            )

        self.__grid_widgets()

    def press(self, but: str) -> None:
        ev = Event()
        ev.keysym = self.__class__.KEYSYM[but] if but in self.__class__.KEYSYM else but
        ev.char = but
        ev.x = 0
        ev.y = 0
        ev.state = 8
        ev.delta = 0
        ev.type = 2
        ev.keycode = ord(but.upper())

        self.__callback(but, ev)

    def __grid_widgets(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        for i, button in enumerate(self.__buttons):
            button.grid(row=i, column=0, sticky="NSEW", pady=5)
            self.grid_rowconfigure(i, weight=1)
