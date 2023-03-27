"""
ui/_template_box.py

Project: BotballUI
Created: 24.03.2023
Author: Lukas Krahbichler
"""

##################################################
#                    Imports                     #
##################################################

from customtkinter import CTkFrame, CTkButton, CTkFont, Variable
from typing import Any, Optional, Union, Callable
from tkinter import Event, Misc
from json import loads


##################################################
#                     Code                       #
##################################################

class TemplateBox(CTkFrame):
    """
    Some buttons for termbox
    """
    __button_var: Variable
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
            button_var: Variable,
            callback: Callable[[str, Event], any],
            *args: Any,
            font: Optional[Union[tuple, CTkFont]] = None,
            **kwargs: Any
    ) -> None:
        super().__init__(master, *args, **kwargs)
        self.configure(width=0, height=0)

        self.__buttons = []
        self.__button_var = button_var
        self.__callback = callback
        self.__font = font

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.__button_var.trace_add("write", self._update_buttons)

    def _update_buttons(self, *_args) -> None:
        buttons: list[tuple[str, str]] = self.__button_var.get()
        print("NEW BUTS", buttons)

        self.grid_rowconfigure("all", weight=0)

        for but in self.__buttons:
            but.grid_forget()
            but.destroy()
            del but

        self.__buttons = []

        for but in buttons:
            self.__buttons.append(
                CTkButton(self, text=but[0], font=self.__font, command=lambda k=but[1]: self.press(k))
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
        for i, button in enumerate(self.__buttons):
            button.grid(row=i, column=0, sticky="NSEW", pady=5, columnspan=2)
            self.grid_rowconfigure(i, weight=1)
