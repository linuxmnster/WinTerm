import os
import sys
import stat
import shutil
import time
import ctypes
import shlex
from pathlib import Path
from datetime import datetime
from . import CLS_check

def home_path():
    try:
        path = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
        os.chdir(path)
    except FileNotFoundError:
        try:
            path = os.path.join(os.path.expanduser("~"), "Desktop")
            os.chdir(path)
        except FileNotFoundError:
            path = os.path.expanduser("~")
            os.chdir(path)
    return path

#sudo
def run_as_admin():
    # Check if the script is already running as admin
    if ctypes.windll.shell32.IsUserAnAdmin() != 0:
        print("Running with admin privileges.")
        return True
    else:
        print("Attempting to run as admin...")
        # Relaunch the script with admin privileges
        script = sys.argv[0]
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, script, None, 1)
        return False

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def pwd():
    print(os.getcwd())

#ls
def ls_command(cmd):
    flags = ''.join(arg.strip('-') for arg in cmd.split()[1:] if arg.startswith('-'))
    show_all = 'a' in flags
    show_long = 'l' in flags
    human = 'h' in flags
    sort_time = 't' in flags
    reverse = 'r' in flags

    try:
        entries = os.listdir()
        if not show_all:
            entries = [f for f in entries if not f.startswith('.')]

        # Sort entries by time or name
        entries.sort(key=lambda f: os.path.getmtime(f) if sort_time else f.lower(), reverse=reverse)

        # Split into directories and files
        dirs = [f for f in entries if os.path.isdir(f)]
        files = [f for f in entries if not os.path.isdir(f)]

        def format_entry(f, is_dir):
            path = os.path.join(os.getcwd(), f)
            stat_info = os.stat(path)
            icon = "📁" if is_dir else "📄"
            name = f"{icon} {f}"
            name = CLS_check.colorize(name, "blue", None, "bold") if is_dir else CLS_check.colorize(name, "white")

            if show_long:
                perms = stat.filemode(stat_info.st_mode)
                size = stat_info.st_size
                if human:
                    for unit in ['B','K','M','G','T']:
                        if size < 1024:
                            break
                        size /= 1024
                    size = f"{size:.1f}{unit}"
                mtime = time.strftime('%b %d %H:%M', time.localtime(stat_info.st_mtime))
                return f"{perms} {size:>6} {mtime} {name}"
            else:
                return name

        for d in dirs:
            print(format_entry(d, True))
        for f in files:
            print(format_entry(f, False))

    except Exception as e:
        print("Error:", e)


#cd
def cd_command(cmd):
    parts = cmd.strip().split(maxsplit=1)
    if len(parts) == 1 or parts[1] == "~":
        path = home_path()
    elif parts[1] == "/":
        path = "C:\\"  
    else:
        path = os.path.abspath(os.path.expanduser(parts[1]))

    try:
        os.chdir(path)
    except FileNotFoundError:
        print(f"❌ Directory not found: {path}")
    except NotADirectoryError:
        print(f"⚠️ Not a directory: {path}")
    except PermissionError:
        print(f"🚫 Permission denied: {path}")
    except Exception as e:
        print(f"⚠️ Error: {e}")

#mkdir
def mkdir_command(cmd):
    raw_args = cmd[len("mkdir"):].strip()
    args = []
    current = ''
    in_quotes = False

    for char in raw_args:
        if char == '"':
            in_quotes = not in_quotes
            continue
        if char == ' ' and not in_quotes:
            if current:
                args.append(current)
                current = ''
        else:
            current += char

    if current:
        args.append(current)

    if not args:
        print("⚠️  mkdir: missing operand")
        return

    for folder in args:
        try:
            # Check if folder already exists
            if os.path.exists(folder):
                print(f"⚠️  mkdir: '{folder}' already exists")
            else:
                os.makedirs(folder)
                print(f"📁 Created: {folder}")
        except Exception as e:
            print(f"⚠️  mkdir: error creating '{folder}': {e}")
            
#rmdir
def rmdir_command(raw_input: str):
    try:
        # Use shlex.split to handle quoted paths like "new folder"
        parts = shlex.split(raw_input)

        if len(parts) <= 1:
            print("⚠️  rmdir: missing operand")
            return

        # First part is 'rmdir', rest are flags or directory names
        args = parts[1:]

        force_flag = False
        directories = []

        for arg in args:
            if arg == "-f":
                force_flag = True
            else:
                directories.append(arg)

        if not directories:
            print("⚠️  No directories specified for removal.")
            return

        for directory in directories:
            try:
                if force_flag:
                    shutil.rmtree(directory)
                    print(f"📁 Directory '{directory}' removed (force).")
                else:
                    os.rmdir(directory)
                    print(f"📁 Directory '{directory}' removed.")
            except OSError as e:
                print(f"⚠️  Failed to remove '{directory}': {e}")

    except ValueError as e:
        print(f"⚠️  Error parsing input: {e}")

#touch
def touch_command(raw_input):
    args = shlex.split(raw_input)  # Handles quotes properly

    if len(args) == 1:
        print("⚠️  touch: missing file operand")
        return

    flags = []
    filenames = []

    # Start from 1 to skip the 'touch' part
    for arg in args[1:]:
        if arg.startswith('-'):
            flags.append(arg)
        else:
            filenames.append(arg)

    # Parse flags
    no_create = '-c' in flags
    change_access = '-a' in flags
    change_mod = '-m' in flags
    use_current_time = not change_access and not change_mod  # default behavior

    current_time = datetime.now().timestamp()

    for file in filenames:
        path = Path(file)
        try:
            if path.exists():
                times = (
                    current_time if change_access or use_current_time else path.stat().st_atime,
                    current_time if change_mod or use_current_time else path.stat().st_mtime,
                )
                os.utime(path, times)
            else:
                if not no_create:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.touch()
        except Exception as e:
            print(f"⚠️  Error creating/updating file '{file}': {e}")

#cat
def cat_command(raw_input: str):
    import re

    args = raw_input.strip().split()
    flags = {
        "-n": False,
        "-b": False,
        "-E": False,
        "-s": False,
        "-T": False,
        "-A": False
    }

    files = []

    # Extract flags and files (handles quotes too)
    joined = raw_input[len("cat"):].strip()
    tokens = re.findall(r'"[^"]*"|\S+', joined)

    for token in tokens:
        if token in flags:
            flags[token] = True
            if token == "-A":
                flags["-E"] = True
                flags["-T"] = True
        else:
            files.append(token.strip('"'))

    if not files:
        print("⚠️  cat: missing operand")
        return

    for filename in files:
        if not os.path.exists(filename):
            print(f"⚠️  cat: {filename}: No such file or directory")
            continue
        if os.path.isdir(filename):
            print(f"⚠️  cat: {filename}: Is a directory")
            continue

        try:
            with open(filename, "r", encoding="utf-8") as f:
                lines = f.readlines()

            output_lines = []
            previous_blank = False
            line_number = 1

            for line in lines:
                show_line = line.rstrip("\n")

                # -s (suppress multiple empty lines)
                if flags["-s"]:
                    if show_line.strip() == "":
                        if previous_blank:
                            continue
                        previous_blank = True
                    else:
                        previous_blank = False

                prefix = ""
                # -b or -n (numbering)
                if flags["-b"] and show_line.strip() != "":
                    prefix = f"{line_number:6}\t"
                    line_number += 1
                elif flags["-n"]:
                    prefix = f"{line_number:6}\t"
                    line_number += 1

                # -T (show tabs)
                if flags["-T"]:
                    show_line = show_line.replace("\t", "^I")

                # -E (show end-of-line $)
                if flags["-E"]:
                    show_line += "$"

                output_lines.append(f"{prefix}{show_line}")

            print("\n".join(output_lines))

        except Exception as e:
            print(f"⚠️  cat: {filename}: {e}")