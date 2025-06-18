import os, sys, shutil, shlex, fileinput
import stat
import time
import ctypes
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
    args = shlex.split(raw_input)[1:]
    if not args:
        print("⚠️  touch: missing file operand")
        return

    atime, mtime = None, None
    no_create = False
    files = []
    i = 0

    while i < len(args):
        arg = args[i]
        if arg in ("-a",): atime = "now"
        elif arg in ("-m",): mtime = "now"
        elif arg in ("-c", "--no-create"): no_create = True
        elif arg in ("-f", "-h", "--no-dereference"): pass
        elif arg.startswith(("-d=", "--date=")):
            try:
                ts = datetime.fromisoformat(arg.split("=", 1)[1]).timestamp()
                atime = mtime = ts
            except: print(f"⚠️  Invalid date: {arg}"); return
        elif arg == "-t":
            i += 1
            try:
                fmt = "%Y%m%d%H%M.%S" if '.' in args[i] else "%Y%m%d%H%M"
                ts = time.mktime(time.strptime(args[i], fmt))
                atime = mtime = ts
            except: print(f"⚠️  Invalid -t timestamp: {args[i]}"); return
        elif arg.startswith(("-r=", "--reference=")):
            ref = arg.split("=", 1)[1]
            try:
                s = os.stat(ref)
                atime, mtime = s.st_atime, s.st_mtime
            except: print(f"⚠️  Reference file not found: {ref}"); return
        elif arg.startswith("-"):
            print(f"⚠️  Unknown flag: {arg}")
        else:
            files.append(arg)
        i += 1

    now = time.time()
    atime = now if atime in ("now", None) else atime
    mtime = now if mtime in ("now", None) else mtime

    for f in files:
        path = Path(f)
        try:
            if path.exists():
                os.utime(path, (atime, mtime))
            elif not no_create:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()
                os.utime(path, (atime, mtime))
        except Exception as e:
            print(f"⚠️  touch: {f}: {e}")


#cat
def cat_command(raw_input):
    args = shlex.split(raw_input)
    if len(args) == 1:
        print("⚠️  cat: missing operand")
        return

    args = args[1:]  # remove 'cat'

    # Redirection (cat > file.txt / >> file.txt / copy files)
    if ">" in args or ">>" in args:
        op = ">>" if ">>" in args else ">"
        op_idx = args.index(op)
        sources = args[:op_idx]
        dest = args[op_idx + 1] if op_idx + 1 < len(args) else None

        if not dest:
            print("⚠️  cat: missing destination file")
            return

        try:
            mode = "a" if op == ">>" else "w"
            if not sources:
                # cat > file.txt or >> file.txt — interactive write
                print(f"✍️  Enter content for '{dest}' (Press Ctrl+Z then Enter to save, Ctrl+C to cancel):")
                try:
                    with open(dest, mode, encoding="utf-8") as f:
                        while True:
                            try:
                                line = input()
                                f.write(line + "\n")
                            except EOFError:
                                break
                    print(f"✅ {'Appended' if mode == 'a' else 'Saved'} to '{dest}'")
                except KeyboardInterrupt:
                    print("\n❌ Aborted.")
                except Exception as e:
                    print(f"❌ Error: {e}")
            else:
                with open(dest, mode, encoding="utf-8") as f_out:
                    for src in sources:
                        if os.path.isfile(src):
                            with open(src, "r", encoding="utf-8", errors="replace") as f:
                                f_out.write(f.read())
                        else:
                            print(f"⚠️  cat: {src}: No such file or not a file")
                print(f"✅ {'Appended' if mode == 'a' else 'Copied'} to '{dest}'")
        except Exception as e:
            print(f"❌ Error: {e}")
        return

    # Flag parsing
    flags = {
        "-A": False, "-b": False, "-E": False,
        "-n": False, "-s": False, "-T": False, "-v": False, "-e": False
    }
    files = []

    for arg in args:
        if arg.startswith("-"):
            for char in arg[1:]:
                key = f"-{char}"
                if key in flags:
                    flags[key] = True
                    if key == "-A":
                        flags["-v"] = flags["-E"] = flags["-T"] = True
                    if key == "-e":
                        flags["-v"] = True
                        flags["-E"] = True
                else:
                    print(f"⚠️  cat: unknown flag: -{char}")
        else:
            files.append(arg)

    for file in files:
        if not os.path.isfile(file):
            print(f"⚠️  cat: {file}: No such file or not a file")
            continue

        try:
            with open(file, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            line_number = 1
            previous_blank = False
            output = []

            for line in lines:
                raw = line.rstrip("\n")

                if flags["-s"] and raw.strip() == "":
                    if previous_blank:
                        continue
                    previous_blank = True
                else:
                    previous_blank = False

                if flags["-v"]:
                    raw = ''.join(
                        c if 32 <= ord(c) <= 126 or c == '\t'
                        else f"^{chr(ord(c) + 64)}" for c in raw
                    )

                if flags["-T"]:
                    raw = raw.replace("\t", "^I")

                if flags["-E"]:
                    raw += "$"

                prefix = ""
                if flags["-b"] and raw.strip():
                    prefix = f"{line_number:6}\t"
                    line_number += 1
                elif flags["-n"]:
                    prefix = f"{line_number:6}\t"
                    line_number += 1

                output.append(prefix + raw)

            print("\n".join(output))

        except Exception as e:
            print(f"⚠️  cat: {file}: {e}")

