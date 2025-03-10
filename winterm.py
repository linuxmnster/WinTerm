from termcolor import colored
import sys
import os

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
cmd_function_call.call("clear")

while True:
    cmd = input(colored("Kira", "red") + colored("@", "white") + colored("WinTerm", "blue")+colored("> ", "white"))
    if cmd == "exit":
        break
    
    elif cmd == "help":
        help.help()

    elif cmd == "help -web":
        help.open_html()

    elif cmd == "man " + cmd[4:]:
        help.man(cmd[4:])

    elif cmd == "rn " + cmd[3:]:
        toolkit.check(cmd[3:])

    elif cmd == "win " + cmd[4:]:
        win.service(cmd[4:])

    else:
        cmd_function_call.call(cmd)

