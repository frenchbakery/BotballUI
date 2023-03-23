"""
_run_frame.py
04. March 2023

Frame shown when "run" is selected

Author:
Nilusink
"""
from concurrent.futures import ThreadPoolExecutor
from ._term_box import TermBox
import customtkinter as ctk
import typing as tp
import os


class WindowConfig(tp.TypedDict):
    appearance_mode: tp.Literal["dark", "light"]
    program_directories: list[str]
    program_ignores: list[str]
    fullscreen: bool
    theme: str


class RunFrame(ctk.CTkFrame):
    """
    main program window
    """
    running: bool = True
    programs: dict[str, str] = ...
    _pool: ThreadPoolExecutor = ...
    _selected_program: tp.Union[str, None] = None
    window_config: WindowConfig = ...

    def __init__(self, window_config: WindowConfig, *args, **kwargs) -> None:
        # mutable defaults
        self.window_config = window_config
        self._err_to_insert = []
        self._to_insert = []
        self.programs = {}

        # init parent class
        super().__init__(*args, **kwargs)

        # ui layout
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.program_button = ctk.CTkButton(
            self,
            text="Run",
            font=("Sans-Serif", 30, "bold"),
            corner_radius=15,
            command=self._run_program,
            fg_color="#3a7ebf",
            height=100,
            width=300,
        )
        self.program_button.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=30,
            pady=10
        )

        # place programs
        self.update_programs()

        self.programs_combo = ctk.CTkComboBox(
            self,
            values=list(self.programs.keys()),
            font=("Sans-Serif", 30),
            command=self._select_program,
            dropdown_font=("Sans-Serif", 30)
        )
        self.programs_combo.grid(row=0, column=0, sticky="ew", padx=30)

        self.std_out = TermBox(self, font=("Sans-Serif", 20))
        self.std_out.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=20,
            pady=20,
            columnspan=2
        )

    def update_programs(self) -> bool:
        """
        update shown programs
        :return: True if new programs
        """
        changed = False
        for program_dir in self.window_config["program_directories"]:
            if os.path.exists(program_dir):
                for directory in [d for d in os.listdir(program_dir) if
                                  os.path.isdir(program_dir + "/" + d)]:

                    program_name = directory.split("/")[-1]
                    program_path = program_dir + "/" + directory

                    if program_name not in self.programs:
                        changed = True
                        self.programs[program_name] = program_path

                        if self._selected_program is None:
                            self._selected_program = program_path

            else:
                print(f"directory doesnt' exist: \"{program_dir}\"")

        return changed

    def _select_program(self, value: str) -> None:
        """
        select program to run
        :param value: programs name
        """
        if value in self.programs:
            self._selected_program = self.programs[value]

    def _run_program(self, *_trash) -> None:
        """
        run a program
        """
        if self._selected_program is not None:
            self._running_program = self.std_out.run_program(
                self._selected_program + "/run/main"
            )

    def _kill_program(self, *_trash) -> None:
        """
        kill the currently running program
        """
        self.std_out.kill_program()

    def update(self) -> None:
        if self.update_programs():
            print("updating: ", list(self.programs.keys()))
            self.programs_combo.configure(values=list(self.programs.keys()))

        self.std_out.update()
        self.program_button.configure(
            text="Kill" if self.std_out.program_running else "Start"
        )
        self.program_button.configure(
            fg_color="#aa3333" if self.std_out.program_running else "#3a7ebf"
        )
        self.program_button.configure(
            command=self._kill_program if self.std_out.program_running
            else self._run_program
        )

    def end(self) -> None:
        """
        close the program
        """
        self.running = False
        self.std_out.end()

    def destroy(self):
        self.end()
