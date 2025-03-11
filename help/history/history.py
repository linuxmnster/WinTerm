import os
import time
from termcolor import colored

# Define the path for the history file
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "command_history.txt")

def save_command(command, executed=True):
    """Save the entered command to a history file with timestamp and execution status."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    status = "executed" if executed else "not_executed"
    with open(HISTORY_FILE, "a") as file:
        file.write(f"{command} | {timestamp} | {status}\n")

def read_history():
    """Read and display the command history in the required format."""
    if not os.path.exists(HISTORY_FILE):
        print(colored("No command history found!", "yellow"))
        return []

    with open(HISTORY_FILE, "r") as file:
        history_data = file.readlines()

    if not history_data:
        print(colored("No command history found!", "yellow"))
        return []

    formatted_history = []
    for index, line in enumerate(history_data, start=1):
        parts = line.strip().split(" | ")
        if len(parts) == 3:
            command, timestamp, status = parts
            color = "green" if status == "executed" else "red"
            formatted_history.append(colored(f"[{index}] {command} | {timestamp} |", color))

    return formatted_history  # ✅ Always return a list

def clear_history():
    """Clear the command history file."""
    open(HISTORY_FILE, "w").close()
    print(colored("Command history cleared!", "green"))
