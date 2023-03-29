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
from typing import Optional, Union
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

    def __init__(self, master: Misc, font: Optional[Union[tuple, CTkFont]] = None, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

        self.__reboot_button = CTkButton(self, text="Reboot", font=font, fg_color="#3a7ebf",
                                         command=lambda: self.__run("sudo reboot"))
        self.__restart_ui_button = CTkButton(self, text="UI-Restart", font=font, fg_color="#3a7ebf",
                                             command=lambda: self.__run("sudo systemctl restart botballui.service"))

        self.__grid_widgets()

    def __run(self, cmd: str) -> None:  # noqa
        system(cmd)

    def __grid_widgets(self) -> None:
        self.__reboot_button.grid(row=0, column=0, sticky="NSEW", padx=30, pady=30)
        self.__restart_ui_button.grid(row=1, column=0, sticky="NSEW", padx=30, pady=30)

        self.grid_rowconfigure("all", weight=1)
        self.grid_columnconfigure("all", weight=1)
