import os
import time
from termcolor import colored

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "command_history.txt")

def save_command(command, executed=True):
    """Save the entered command to history with execution status."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    status = "executed" if executed else "not_executed"
    with open(HISTORY_FILE, "a") as file:
        file.write(f"{command} | {timestamp} | {status}\n")

def read_history():
    """Read and display executed command history with colors and formatting."""
    if not os.path.exists(HISTORY_FILE):
        print(colored("No command history found!", "yellow"))
        return

    with open(HISTORY_FILE, "r") as file:
        history_data = file.readlines()

    if not history_data:
        print(colored("No command history found!", "yellow"))
        return

    print()
    for index, line in enumerate(history_data, start=1):
        parts = line.strip().split(" | ")
        if len(parts) == 3:
            command, timestamp, status = parts
            color = "green" if status == "executed" else "red"
            print(colored(f"[{index}] {command} | {timestamp} |", color))

def clear_history():
    """Clear command history."""
    open(HISTORY_FILE, "w").close()
