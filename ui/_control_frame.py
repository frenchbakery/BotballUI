"""
ui/_control_frame.py

Project: BotballUI
Created: 29.03.2023
Author: Lukas Krahbichler
"""

##################################################
#                    Imports                     #
##################################################

from customtkinter import CTkFrame, CTkButton, CTkFont
from typing import Optional, Union, Callable, Any
from .kill import kill_running
from tkinter import Misc
from os import system


##################################################
#                     Code                       #
##################################################

class ControlFrame(CTkFrame):
    """
    ControlFrame for restart, systemctl
    """

    __reboot_button: CTkButton
    __restart_ui_button: CTkButton

    # Shutdown, Reboot, Controler reset, restart_ui, kill all run/main

    __BUTTONS: list[list[tuple[str, Callable[[Any], Any]]]]

    def __init__(
            self,
            master: Misc,
            font: Optional[Union[tuple, CTkFont]] = None,
            *args,
            **kwargs
    ) -> None:
        super().__init__(master, *args, **kwargs)

        self.__BUTTONS = [
            [
                (
                    "Shutdown",
                    lambda: self.__run("sudo shutdown now")
                ),
                (
                    "Reboot",
                    lambda: self.__run("sudo reboot")
                )
            ],
            [
                (
                    "Controller reset",
                    lambda: self.__run("/home/access/wallaby_reset_coproc")
                ),
                (
                    "Restart UI",
                    lambda: self.__run("sudo systemctl restart botballui.service")
                )
            ],
            [
                (
                    "Kill Running",
                    lambda: kill_running()
                )
            ]
        ]

        for icol, col in enumerate(self.__BUTTONS):
            for irow, row in enumerate(col):
                tmp = CTkButton(self, text=row[0], command=row[1], corner_radius=50,
                                font=font)
                tmp.grid(column=icol, row=irow, sticky="NSEW", padx=10, pady=10)

        self.grid_columnconfigure("all", weight=1)
        self.grid_rowconfigure("all", weight=1)

    def __run(self, cmd: str) -> None:  # noqa
        system(cmd)
