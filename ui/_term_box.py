"""
_term_box.py
11. March 2023

A tkinter texbox, but also a terminal

Author:
Nilusink
"""
from concurrent.futures import ThreadPoolExecutor
from traceback import format_exc
from ._tk_term_colors import *
import customtkinter as ctk
from time import sleep
import typing as tp
import subprocess
import signal
import os


class TermBox(ctk.CTkTextbox):
    """
    Just like a tkinter texbox, but wired to a running program
    """
    _running_program: tp.Union[subprocess.Popen, None] = None
    _program_running: bool = False
    _to_insert: list[tuple[str, str]] = ...
    _err_to_insert: list[tuple[str, str]] = ...
    running = True

    def __init__(self, *args, proc: tp.Union[subprocess.Popen, None] = None, **kwargs):
        self._running_program = proc
        self._to_insert: list[tuple[str, str]] = []
        self._err_to_insert: list[tuple[str, str]] = []

        super().__init__(*args, **kwargs)

        for color in SIMPLE_COLORS:
            if color[0] == "Reset":
                continue

            self._textbox.tag_configure(color[0], foreground=color[0])

        # threads
        self._pool = ThreadPoolExecutor(max_workers=1)
        self._pool.submit(self._update_proc)

    def _update_proc(self) -> None:
        """
        thread. Updates the programs stdout / stderr / stdin
        """
        curr_tag = ""
        try:
            while self.running:
                if self._running_program is not None:
                    self._program_running = self._running_program.poll() is None

                    byte_char = self._running_program.stdout.read(1)
                    if byte_char:
                        if byte_char[0] == 27:  # font control character
                            curr_tag = read_color_code(self._running_program.stdout)
                            continue

                        self._to_insert.append((byte_char.decode("utf-8"), curr_tag))
                        continue

                    # only read error messages when there is no stdout to read anymore
                    err_char = self._running_program.stderr.read(1)
                    if err_char:
                        self._err_to_insert.append((err_char.decode("utf-8"), "#75020c"))

                        # read until nothing more to read
                        while err_char := self._running_program.stderr.read(1):
                            self._err_to_insert.append((err_char.decode("utf-8"), "#75020c"))

                        self._err_to_insert.append(("", ""))  # end code

                sleep(.0001)  # i know python is slow, but believe me, this does actually make a difference

        except Exception:
            print("program exited: ", format_exc())
            raise

    def kill_program(self) -> None:
        """
        kill the currently running program
        """
        if self._running_program is not None:
            self._running_program.send_signal(signal.SIGTERM)

    def run_program(
            self,
            command: str | bytes | os.PathLike[str] | os.PathLike[bytes] | tp.Sequence[
                str | bytes | os.PathLike[str] | os.PathLike[bytes]]
            ) -> subprocess.Popen:
        """
        run a program
        """
        self.delete(0.0, ctk.END)  # clear output texbox
        self._running_program = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE
        )
        return self._running_program

    def update(self) -> None:
        """
        update the textbox text insertion
        """
        # insert stdout into textbox
        # group by color
        tmp = self._to_insert.copy()
        to_insert: list[list[str, str]] = []
        self._to_insert.clear()
        curr_flag = None
        for line in tmp:
            char, flag = line
            if flag == curr_flag:
                to_insert[-1][0] += char
                continue

            curr_flag = flag
            to_insert.append([char, flag])

        for s in to_insert:
            self.insert(ctk.END, *s)

        # error messages
        # only insert if a whole message is present
        if not (self._program_running or self._to_insert) and self._err_to_insert and self._err_to_insert[-1][0] == "":
            # add newline for better readability
            tmp = [("\n", "")] + self._err_to_insert.copy()[:-1]
            to_insert: list[list[str, str]] = []
            self._err_to_insert.clear()
            curr_flag = None
            for line in tmp:
                char, flag = line
                if flag == curr_flag:
                    to_insert[-1][0] += char
                    continue

                curr_flag = flag
                to_insert.append([char, flag])

            for s in to_insert:
                self.insert(ctk.END, *s)

    def update_process(self, proc: subprocess.Popen):
        """
        update the currently running process
        :param proc: process
        """
        self.delete(0.0, ctk.END)  # clear output texbox
        self._running_program = proc

    @property
    def program_running(self) -> bool:
        """
        program status
        """
        return self._program_running

    def end(self):
        """
        close all threads
        :return:
        """
        self.kill_program()
        self.running = False

    def destroy(self):
        self.end()
        super().destroy()
