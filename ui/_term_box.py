"""
_term_box.py
11. March 2023

A tkinter texbox, but also a terminal

Author:
Nilusink
"""
from ._tk_term_colors import SIMPLE_COLORS, read_color_code
from concurrent.futures import ThreadPoolExecutor
from traceback import format_exc
import customtkinter as ctk
from time import sleep
import typing as tp
import subprocess
import signal
import string
import os


class ControlKeys(tp.TypedDict):
    ctrl: bool
    shift: bool


class TermBox(ctk.CTkTextbox):
    """
    Just like a tkinter texbox, but wired to a running program
    """
    _running_program: tp.Union[subprocess.Popen, None] = None
    _program_running: bool = False
    _to_insert: list[tuple[str, str]] = ...
    _err_to_insert: list[tuple[str, str]] = ...
    _control_keys: ControlKeys = ...
    running = True

    def __init__(
            self, *args, proc: tp.Union[subprocess.Popen, None] = None,
            **kwargs
    ):
        self._running_program = proc
        self._to_insert: list[tuple[str, str]] = []
        self._err_to_insert: list[tuple[str, str]] = []
        self._control_keys = {
            "ctrl": False, "shift": False
        }

        super().__init__(*args, **kwargs)

        for color in SIMPLE_COLORS.values():
            if color[0] == "Reset":
                continue

            self._textbox.tag_configure(color[0], foreground=color[0])

        # threads
        self._pool = ThreadPoolExecutor(max_workers=1)
        self._pool.submit(self._update_proc)

        # modify binds
        self.bind("<KeyPress>", self._update_stdin)
        self.bind("<KeyRelease>", self._on_key_up)

    def _update_stdin(self, event) -> None:
        """
        update the process on key input
        """
        if not self._program_running:
            return

        # ctrl is held
        if self._control_keys["ctrl"]:
            if event.keysym == "c":
                self._running_program.send_signal(signal.SIGINT)

            elif event.keysym == "l":
                self.delete(0.0, ctk.END)

            return

        if event.keysym in string.ascii_letters:
            print(event.keysym, end="")
            self._running_program.stdin.write(event.keysym.encode("utf-8"))

        elif event.keysym.lower() == "return":
            print(b"\x0d\x0a".decode(), end="")
            self._running_program.stdin.write(b"\x0a\x20")  # cr + lf

        elif event.keysym.lower() == "backspace":
            print(b"\x08".decode(), end="")
            self._running_program.stdin.write(b"\x08")

        elif event.keysym.lower() == "space":
            print(b"\x20".decode(), end="")
            self._running_program.stdin.write(b"\x20")

        elif event.keysym.startswith("Control"):
            self._control_keys["ctrl"] = True
            return

        elif event.keysym.startswith("Shift"):
            self._control_keys["shift"] = True
            return

        else:
            print(event.keysym)
            print(event.char, end="")
            self._running_program.stdin.write(event.char.encode())

        self._running_program.stdin.flush()

    def _on_key_up(self, event) -> None:
        """
        handles key up events
        """
        if event.keysym.startswith("Control"):
            self._control_keys["ctrl"] = False
            return

        elif event.keysym.startswith("Shift"):
            self._control_keys["shift"] = False
            return

    def _update_proc(self) -> None:
        """
        thread. Updates the programs stdout / stderr / stdin
        """
        curr_tag = ""
        try:
            while self.running:
                if self._running_program is not None:
                    self._program_running = self._running_program.poll() is \
                                            None

                    byte_char = self._running_program.stdout.read(1)
                    if byte_char:
                        if byte_char[0] == 27:  # font control character
                            curr_tag = read_color_code(
                                self._running_program.stdout
                            )
                            continue

                        self._to_insert.append(
                            (byte_char.decode("utf-8"), curr_tag)
                        )
                        continue

                    # only read error messages when
                    # there is no stdout to read anymore
                    err_char = self._running_program.stderr.read(1)
                    if err_char:
                        self._err_to_insert.append(
                            (err_char.decode("utf-8"), SIMPLE_COLORS["red"][0])
                        )

                        # read until nothing more to read
                        while err_char := self._running_program.stderr.read(1):
                            self._err_to_insert.append(
                                (err_char.decode("utf-8"),
                                 SIMPLE_COLORS["red"][0])
                            )

                        self._err_to_insert.append(("", ""))  # end code

                # I know python is slow, but believe me,
                # this does actually make a difference
                sleep(.005)

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
            self, command: tp.Union[
                str, bytes, os.PathLike[str], os.PathLike[bytes], tp.Sequence[
                    tp.Union[
                        str, bytes, os.PathLike[str], os.PathLike[bytes]]]]
    ) -> subprocess.Popen:
        """
        run a program
        """
        self.delete(0.0, ctk.END)  # clear output texbox
        self._running_program = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            stdin=subprocess.PIPE, )
        return self._running_program

    def _insert_grouped(self, to_insert: list[tuple[str, str]]) -> None:
        """
        groups by tag and inserts into texbox
        :param to_insert: ungrouped chars / tags
        """
        grouped: list[list[str, str]] = []
        curr_flag = None
        for line in to_insert:
            char, flag = line
            if flag == curr_flag:
                grouped[-1][0] += char
                continue

            curr_flag = flag
            grouped.append([char, flag])

        for s in grouped:
            self.insert(ctk.END, *s)

        if grouped:
            # scroll to end
            self.see("end")

    def update(self) -> None:
        """
        update the textbox text insertion
        """
        # insert stdout into textbox
        self._insert_grouped(self._to_insert.copy())
        self._to_insert.clear()

        # only insert if a whole error message is present
        if not (
                self._program_running or self._to_insert) and \
                self._err_to_insert and \
                self._err_to_insert[-1][0] == "":
            # add newline for better readability
            tmp = [("\n", "")] + self._err_to_insert.copy()[:-1]
            self._insert_grouped(tmp)
            self._err_to_insert.clear()

    def update_process(self, proc: subprocess.Popen):
        """
        update the currently running process
        :param proc: subprocess popen process
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
