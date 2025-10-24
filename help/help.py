# help/help.py

import os
import webbrowser
from . import context

def trigger_help(raw_input=None):
    """
    Triggered when user types 'help' in CLI.
    If raw_input is 'help -web', opens web documentation.
    Otherwise, prints the command tables.
    """
    if raw_input and raw_input.strip().lower() == "help -web":
        open_web_docs()
    else:
        context.show_commands_table()

def open_web_docs():
    """
    Opens the web documentation located in help/web/index.html
    """
    # Get the absolute path of this help.py file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    web_path = os.path.join(base_dir, "web", "index.html")

    if os.path.exists(web_path):
        webbrowser.open(f"file://{web_path}")
    else:
        print("Web documentation not found at help/web/index.html.")
