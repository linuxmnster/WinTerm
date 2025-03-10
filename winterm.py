from termcolor import colored
import sys
import os
import signal
from time import sleep

home = os.path.expanduser("~")
os.chdir(home)

cli_path = os.path.join(os.path.dirname(__file__), "CLI")
sys.path.append(cli_path)

help_path = os.path.join(os.path.dirname(__file__), "help")
sys.path.append(help_path)

tools_path = os.path.join(os.path.dirname(__file__), "tools")
sys.path.append(tools_path)

services = os.path.join(os.path.dirname(__file__), "services")
sys.path.append(services)

import help
from CLI import cmd_function_call
from tools import toolkit
from services import win

# Flag to track if a process is running
running_process = False

def signal_handler(sig, frame):
    """Handle Ctrl+C behavior based on whether a process is running."""
    global running_process
    if running_process:
        print("\n" + colored("Process interrupted. Press Ctrl+C again to exit.", "yellow"))
        running_process = False  # Reset flag
    else:
        print("\n" + colored("Exiting...", "red"))
        sleep(1)
        sys.exit()  # Exit the program

# Set up SIGINT handler
signal.signal(signal.SIGINT, signal_handler)

cmd_function_call.call("clear")

while True:
    try:
        cmd = input(colored("Kira", "red") + colored("@", "white") + colored("WinTerm", "blue") + colored("> ", "white")).strip()

        # Ignore empty commands (only spaces or enter)
        if not cmd:
            continue  # Just go to the next prompt

        if cmd == "exit":
            break
        
        elif cmd == "help":
            help.help()

        elif cmd == "help -web":
            help.open_html()

        elif cmd.startswith("man "):
            help.man(cmd[4:])

        elif cmd.startswith("rn "):
            toolkit.check(cmd[3:])

        elif cmd.startswith("win "):
            win.service(cmd[4:])

        else:
            running_process = True  # A command is being executed
            cmd_function_call.call(cmd)
            running_process = False  # Reset after execution

    except KeyboardInterrupt:
        signal_handler(None, None)  # Call handler manually
