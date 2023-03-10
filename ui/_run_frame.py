"""
_run_frame.py
04. March 2023

Frame shown when "run" is selected

Author:
Nilusink
"""
from concurrent.futures import ThreadPoolExecutor
from ._tk_term_colors import cmd_to_tk, SIMPLE_COLORS, COMPLEX_COLORS
from subprocess import Popen, PIPE
from traceback import format_exc
import customtkinter as ctk
from time import sleep
import typing as tp
import signal
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
    _running_program: tp.Union[Popen, None] = None
    window_config: WindowConfig = ...
    _program_running: bool = False
    _to_insert: list[tuple[str, str]] = ...

    def __init__(self, window_config: WindowConfig, *args, **kwargs) -> None:
        # threads
        self._pool = ThreadPoolExecutor(max_workers=1)
        self._pool.submit(self._stdout_update)

        # mutable defaults
        self.window_config = window_config
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
        self.program_button.grid(row=0, column=1, sticky="ew", padx=30, pady=10)

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

        self.std_out = ctk.CTkTextbox(self, font=("Sans-Serif", 20))
        self.std_out.grid(row=1, column=0, sticky="nsew", padx=20, pady=20, columnspan=2)

        for color in SIMPLE_COLORS:
            if color[0] == "Reset":
                continue

            self.std_out._textbox.tag_configure(color[0], foreground=color[0])

    def update_programs(self) -> bool:
        """
        update shown programs
        :return: True if new programs
        """
        changed = False
        for program_dir in self.window_config["program_directories"]:
            if os.path.exists(program_dir):
                for directory in os.listdir(program_dir):
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
            self.std_out.delete(0.0, ctk.END)  # clear output texbox
            self._running_program = Popen(self._selected_program + "/run/main", stdout=PIPE)

    def _kill_program(self, *_trash) -> None:
        """
        kill the currently running program
        """
        if self._running_program is not None:
            self._running_program.send_signal(signal.SIGTERM)

    def _stdout_update(self) -> None:
        """
        thread, gets programs stdout and writes it into the textbox
        """
        curr_tag = ""
        try:
            while self.running:
                if self._running_program is not None:
                    self._program_running = self._running_program.poll() is None

                    if 1: #self._program_running:
                        byte_char = self._running_program.stdout.read(1)

                        if byte_char:
                            if byte_char[0] == 27:  # font control character
                                curr = b""
                                n_char = self._running_program.stdout.read(1)
                                while n_char[0] != 109:
                                    curr += n_char
                                    n_char = self._running_program.stdout.read(1)

                                    if len(curr) > 10:
                                        raise ValueError

                                control_code = 0
                                s_curr = curr.decode().lstrip("[").rstrip("m")
                                if ";" in s_curr:
                                    control_code, color = s_curr.split(";")

                                else:
                                    color = s_curr

                                tk_col = cmd_to_tk(int(color), int(control_code))
                                if tk_col.lower() in ("reset", "undefined", "unsuported"):
                                    curr_tag = ""
                                    continue

                                curr_tag = tk_col
                                continue

                            self._to_insert.append((byte_char.decode("utf-8"), curr_tag))

                sleep(.02)

        except Exception:
            print(format_exc())
            raise

    def update(self) -> None:
        if self.update_programs():
            self.programs_combo.configure(values=list(self.programs.keys()))

        tmp = self._to_insert.copy()
        self._to_insert.clear()
        for line in tmp:
            self.std_out.insert(ctk.END, *line)

        self.program_button.configure(text="Kill" if self._program_running else "Start")
        self.program_button.configure(fg_color="#aa3333" if self._program_running else "#3a7ebf")
        self.program_button.configure(command=self._kill_program if self._program_running else self._run_program)

    def end(self) -> None:
        """
        close the program
        """
        self.running = False
        self._kill_program()
