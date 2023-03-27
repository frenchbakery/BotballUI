"""
ui/_keyboard_frame.py

Project: BotballUI
Created: 24.03.2023
Author: Lukas Krahbichler
"""

##################################################
#                    Imports                     #
##################################################

from customtkinter import CTkFrame, Variable, CTkEntry, CTkFont, CTkLabel
from typing import Any, TypedDict, Literal, Optional, Union
from tkinter import Misc, Entry


##################################################
#                     Code                       #
##################################################

class WindowConfig(TypedDict):
    appearance_mode: Literal["dark", "light"]
    program_directories: list[str]
    program_ignores: list[str]
    keyboard: list[tuple[str, str]]
    keyboard_var: Variable
    fullscreen: bool
    theme: str


class KEntry(CTkEntry):
    def get_entry(self) -> Entry:
        return self._entry


class KeyboardFrame(CTkFrame):
    """
    Keyboard settings
    """
    __entries: list[tuple[KEntry, KEntry]]

    __window_config: WindowConfig
    __config_path: str
    __font: Optional[Union[tuple, CTkFont]]

    __top_label: CTkLabel
    __top_key: CTkLabel

    def __init__(
            self,
            master: Misc,
            window_config: WindowConfig,
            config_path: str,
            font: Optional[Union[tuple, CTkFont]] = None,
            *args: Any,
            **kwargs: Any) -> None:
        super().__init__(master, *args, **kwargs)

        self.__window_config = window_config
        self.__config_path = config_path
        self.__font = font

        self.__entries = []

        self.__top_label = CTkLabel(self, text="Button-Label:", font=font)
        self.__top_key = CTkLabel(self, text="Key:", font=font)

        self.grid_columnconfigure((0, 1), weight=1)

        self._create_entries()
        self._update()

    def _update(self, *_args) -> None:
        if self.__entries[-1][0].get() != "" or self.__entries[-1][1].get() != "":
            self._add_entry()

        dels: list[tuple[KEntry, KEntry]] = []
        for entry in self.__entries[:-1]:
            if entry[0].get() == "" and entry[1].get() == "" \
                    and self.focus_get() != entry[0].get_entry() and self.focus_get() != entry[1].get_entry():
                dels.append(entry)

            if len(entry[1].get()) > 1:
                let: str = entry[1].get()[-1:]
                entry[1].delete(0, "end")
                entry[1].insert(0, let)

        for d in dels:
            self.__entries.remove(d)

        self.__grid_widgets()

    def _add_entry(self, text1: str = "", text2: str = "") -> None:
        a, b = Variable(), Variable()
        self.__entries.append((
            KEntry(self, font=self.__font, textvariable=a),
            KEntry(self, font=self.__font, textvariable=b)
        ))

        self.__entries[-1][0].insert(0, text1)
        self.__entries[-1][1].insert(0, text2)

        a.trace_add("write", self._update)
        b.trace_add("write", self._update)

        self.__entries[-1][0].bind("<FocusOut>", self._update)
        self.__entries[-1][1].bind("<FocusOut>", self._update)

    def __grid_widgets(self) -> None:
        self.grid_rowconfigure("all", weight=0)

        for widget in self.winfo_children():
            if isinstance(widget, CTkEntry):
                widget.grid_forget()

        self.__top_label.grid(row=0, column=0, sticky="NSEW")
        self.__top_key.grid(row=0, column=1, sticky="NSEW")

        for i, entry in enumerate(self.__entries):
            entry[0].grid(row=i+1, column=0, sticky="NSEW")
            entry[1].grid(row=i+1, column=1, sticky="NSEW")

        self.grid_rowconfigure("all", weight=1)

    def _create_entries(self) -> None:
        for i, kb in enumerate(self.__window_config["keyboard_var"].get()[:-1]):
            self._add_entry(kb[0], kb[1])

    def grid_forget(self) -> None:
        super().grid_forget()

        new_kb: list[tuple[str, str]] = []

        for entry in self.__entries:
            new_kb.append((entry[0].get(), entry[1].get()))

        new_kb = new_kb[:-1] + [("Return", "\n")]

        self.__window_config["keyboard"] = new_kb
        self.__window_config["keyboard_var"].set(new_kb)



