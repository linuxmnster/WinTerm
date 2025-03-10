import os
import webbrowser

def help(filename="manuals/cmd_help.txt"):
    script_dir = os.path.dirname(os.path.abspath(__file__))  
    file_path = os.path.join(script_dir, filename)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read().strip()
            print(content)
    except FileNotFoundError:
        print(f"[-] Error: File '{filename}' not found in {script_dir}")
    except Exception as e:
        print(f"[-] Error: {e}")

def man(cmd):
    script_dir = os.path.dirname(os.path.abspath(__file__))  
    file_path = os.path.join(script_dir, "manuals/cmds/"+cmd+".txt")
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read().strip()
            print()
            print(content)
            print()
    except FileNotFoundError:
        print(f"[-] Error: Command '{cmd}' Not Found!")
    except Exception as e:
        print(f"[-] Error: {e}")


def open_html(filename="commands.html"):
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get script directory
    file_path = os.path.join(script_dir, "help_web/"+filename)  # Construct full path

    if not file_path.endswith(".html"):
        print("[-] Error: Only .html files can be opened.")
        return
    
    if os.path.exists(file_path):
        webbrowser.open(f"file://{file_path}")  # Open in default web browser
        print(f"[+] Opening Documentation in the browser...")
    else:
        print(f"[-] Error: File '{filename}' not found.")

