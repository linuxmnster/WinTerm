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

from CLI import cmd_function_call
import help
from tools import toolkit, win

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

    elif cmd == "tool " + cmd[5:]:
        toolkit.check(cmd[5:])

    elif cmd == "win " + cmd[4:]:
        win.service(cmd[4:])

    else:
        cmd_function_call.call(cmd)

