import os
import time
from termcolor import colored

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "command_history.txt")

def save_command(command):
    """Save the entered command to history."""
    try:
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)  # Ensure directory exists
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(HISTORY_FILE, "a", encoding="utf-8") as file:
            file.write(f"{command} | {timestamp}\n")  # ✅ No more EXECUTED/NOT_EXECUTED
    except Exception as e:
        print(colored(f"Error saving history: {e}", "red"))

def read_history():
    """Read and display command history with colors and formatting."""
    if not os.path.exists(HISTORY_FILE) or os.stat(HISTORY_FILE).st_size == 0:
        print(colored("No command history found!", "yellow"))
        return

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            history_data = file.readlines()

        print("\n" + colored("Command History:", "cyan", attrs=["bold"]))
        print(colored("=" * 50, "white"))

        for index, line in enumerate(history_data, start=1):
            parts = line.strip().split(" | ")
            if len(parts) == 2:
                command, timestamp = parts
                print(f"{colored(f'[{index:2d}]', 'blue')} {colored(command.ljust(20), 'white')} | {colored(timestamp, 'yellow')}")

        print(colored("=" * 50, "white"))
    except Exception as e:
        print(colored(f"Error reading history: {e}", "red"))

def clear_history():
    """Clear command history."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            file.truncate(0)  # Clears the file
        print(colored("Command history cleared!", "green"))
    except Exception as e:
        print(colored(f"Error clearing history: {e}", "red"))
