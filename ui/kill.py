import subprocess
import platform
import signal
import os


SEARCH_FOR: str = "run/main"


def strip_pid(ps_line: str) -> int:
    """
    removes all unwanted string stuff from a ps process output line
    """
    parts = ps_line.split(" ")
    for part in parts:
        if part.isdigit():
            return int(part)


def get_running_pids(identifier: str = SEARCH_FOR) -> list[int]:
    """
    get the pids of all running processes
    """
    if platform.system() == "linux":
        process_output = subprocess.check_output(["ps", "-ax"]).decode()
        return [strip_pid(line) for line in process_output.split("\n")
                if identifier in line]
    return []


def get_n_running() -> int:
    """
    get the number of running processes
    """
    return len(get_running_pids())


def kill_running(sig: signal.signal = signal.SIGINT) -> None:
    """
    kill all running programs

    :param sig: signal to send
    """
    for pid in get_running_pids():
        os.kill(pid, sig)
