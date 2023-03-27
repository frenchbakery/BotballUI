"""
main.py
04. March 2023

<description>

Author:
Nilusink
"""
from ui import RunFrame, SettingsFrame, KeyboardFrame
import customtkinter as ctk
import typing as tp
import json
import os


# types
class WindowConfig(tp.TypedDict):
    appearance_mode: tp.Literal["dark", "light"]
    program_directories: list[str]
    program_ignores: list[str]
    keyboard_var: ctk.Variable
    keyboard: list[tuple[str, str]]
    fullscreen: bool
    theme: str


CONFIG_PAH: str = "./config.json"
WINDOW_CONFIG: WindowConfig = {
    "appearance_mode": "dark",
    "program_directories": [
        "/home/access/projects/"
    ],
    "program_ignores": [],
    "theme": "dark-blue",
    "fullscreen": True,
    "keyboard": [
        ("s", "s"),
        ("a", "a"),
        ("Return", "\n")
    ]
}


# try to load config
if os.path.exists(CONFIG_PAH):
    with open(CONFIG_PAH, "r") as inp:
        config: WindowConfig = json.load(inp)

    for key, value in config.items():
        WINDOW_CONFIG[key] = value


# write adjusted config to make sure every key is present
with open(CONFIG_PAH, "w") as out:
    json.dump(WINDOW_CONFIG, out, indent=4)


# display configuration
if os.environ.get('DISPLAY', '') == '':
    print("no displays found. available: ")
    os.system('(cd /tmp/.X11-unix && for x in X*; do echo ":${x#X}"; done)')
    print('Using :0')
    os.environ.__setitem__('DISPLAY', ':0')


# theme
ctk.set_appearance_mode(WINDOW_CONFIG["appearance_mode"])
ctk.set_default_color_theme(WINDOW_CONFIG["theme"])


class Window(ctk.CTk):
    """
    main program window
    """
    __running: bool = True

    __frames: dict[str, tp.Union[RunFrame, SettingsFrame, KeyboardFrame, ctk.CTkFrame]]
    _FRAME_SEQUENCE: list[str] = ["Run", "Settings", "Keyboard"]

    def __init__(self) -> None:
        # init parent class
        super().__init__()

        WINDOW_CONFIG["keyboard_var"] = ctk.Variable()
        WINDOW_CONFIG["keyboard_var"].set(WINDOW_CONFIG["keyboard"])

        self.title("BotUI")
        self.attributes("-fullscreen", WINDOW_CONFIG["fullscreen"])
        if "-zoomed" in self.attributes():
            self.attributes("-zoomed", True)
        else:
            self.state("zoomed")

        self.minsize(500, 300)

        # events
        self.protocol("WM_DELETE_WINDOW", self.end)
        # ui layout
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        sb = ctk.CTkSegmentedButton(
            self,
            values=self._FRAME_SEQUENCE,
            font=("Sans-Serif", 30),
            command=self._change_frame
        )
        sb._select_button_by_value("Run")
        sb.grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            self,
            text="Quit",
            fg_color="#aa3333",
            hover_color="#ff0000",
            command=self.end,
            font=("Sans-Serif", 30)
        ).grid(row=0, column=1)

        self.__frames = {
            "Run": RunFrame(WINDOW_CONFIG, self, corner_radius=30),
            "Settings": SettingsFrame(WINDOW_CONFIG, CONFIG_PAH, self, corner_radius=30),
            "Keyboard": KeyboardFrame(self, WINDOW_CONFIG, CONFIG_PAH, font=("Sans-Serif", 30), corner_radius=30)
        }

        self._change_frame("Run")

    def _change_frame(self, value: tp.Literal["Run", "Settings"]) -> None:
        """
        change the currently displayed frame
        """
        for frame in self.__frames:
            if self.__frames[frame] != self.__frames[value]:
                self.__frames[frame].grid_forget()

        self.__frames[value].grid(
                row=1,
                column=0,
                padx=30,
                pady=30,
                sticky="nsew",
                columnspan=2
            )

    def mainloop(self) -> None:
        """
        run the program
        """
        while self.__running:
            self.__frames["Run"].update()
            super().update_idletasks()
            super().update()

    def end(self, *_trash) -> None:
        """
        close the program
        """
        self.__running = False
        self.__frames["Run"].end()
        self.destroy()
        exit(0)


if __name__ == '__main__':
    w = Window()
    w.mainloop()
