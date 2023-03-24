"""
_settings_frame.py
04. March 2023

window settings

Author:
Nilusink
"""
import customtkinter as ctk
import typing as tp
import json


class WindowConfig(tp.TypedDict):
    appearance_mode: tp.Literal["dark", "light"]
    program_directories: list[str]
    program_ignores: list[str]
    fullscreen: bool
    theme: str


class SettingsFrame(ctk.CTkFrame):
    window_config: WindowConfig = ...
    config_path: str = ...

    def __init__(
            self,
            window_config: WindowConfig,
            config_path: str,
            *args,
            **kwargs
    ) -> None:
        self.window_config = window_config
        self.config_path = config_path

        super().__init__(*args, **kwargs)

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        # settings
        # appearance
        ctk.CTkLabel(
            self,
            text="Appearance",
            font=("Sans-Serif", 30)
        ).grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        tmp = ctk.CTkComboBox(
            self,
            values=["dark", "light"],
            font=("Sans-Serif", 30),
            command=self.update_appearance,
            dropdown_font=("Sans-Serif", 30),
        )
        tmp.set(self.window_config["appearance_mode"])
        tmp.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # theme
        ctk.CTkLabel(
            self,
            text="Theme",
            font=("Sans-Serif", 30)
        ).grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        tmp = ctk.CTkComboBox(
            self,
            values=["dark-blue", "blue", "green"],
            font=("Sans-Serif", 30),
            command=self.update_theme,
            dropdown_font=("Sans-Serif", 30),
        )
        tmp.set(self.window_config["theme"])
        tmp.grid(row=1, column=1, sticky="nsew")

        # fullscreen
        ctk.CTkLabel(
            self,
            text="Fullscreen",
            font=("Sans-Serif", 30)
        ).grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.fullscreen_var = ctk.BooleanVar(value=window_config["fullscreen"])
        ctk.CTkSwitch(
            self,
            text="",
            variable=self.fullscreen_var,
            onvalue=True,
            offvalue=False,
            switch_height=30,
            switch_width=50,
            command=self.update_fullscreen
        ).grid(row=2, column=1, sticky="nsew", padx=10, pady=10)

        # include directories
        ctk.CTkLabel(
            self,
            text="Directories",
            font=("Sans-Serif", 30)
        ).grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        tmp = ctk.CTkTextbox(self, font=("Sans-Serif", 20), height=60)
        for directory in self.window_config["program_directories"]:
            tmp.insert(ctk.END, directory + "\n")
        tmp.grid(row=3, column=1, sticky="ew", pady=5, padx=10)

        # ignores
        ctk.CTkLabel(
            self,
            text="Ignores",
            font=("Sans-Serif", 30)
        ).grid(row=4, column=0, sticky="nsew", padx=10, pady=10)
        tmp = ctk.CTkTextbox(self, font=("Sans-Serif", 20), height=60)
        for directory in self.window_config["program_ignores"]:
            tmp.insert(ctk.END, directory + "\n")
        tmp.grid(row=4, column=1, sticky="ew", pady=10, padx=10)

    def update_appearance(self, value: tp.Literal["dark", "light"]) -> None:
        """
        update the appearance variable
        :param value: new appearance
        """
        self.window_config["appearance_mode"] = value
        ctk.set_appearance_mode(value)
        self.update_config()

    def update_theme(
            self,
            value: tp.Literal["dark-blue", "blue", "green"]
    ) -> None:
        """
        update the appearance variable
        :param value: new appearance
        """
        self.window_config["theme"] = value
        ctk.set_default_color_theme(value)
        self.update_config()

    def update_fullscreen(self) -> None:
        """
        update the fullscreen variable
        """
        self.window_config["fullscreen"] = self.fullscreen_var.get()
        self.master.attributes("-fullscreen", self.window_config["fullscreen"])
        self.update_config()

    def update_config(self) -> None:
        """
        update the config file
        """
        with open(self.config_path, "w") as out:
            json.dump(self.window_config, out, indent=4)
