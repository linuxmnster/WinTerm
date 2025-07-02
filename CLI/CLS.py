import os, sys, shutil, shlex, glob
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

#rm
def rm_command(raw_input):
    args = shlex.split(raw_input)[1:]  # remove 'rm'

    flags = {
        "-f": False, "-i": False, "-I": False,
        "-r": False, "-d": False, "-v": False
    }

    targets = []

    # Parse flags and expand wildcards
    for arg in args:
        if arg.startswith("-"):
            for char in arg[1:]:
                key = f"-{char}"
                if key in flags:
                    flags[key] = True
                else:
                    print(f"⚠️  rm: unknown option -- {char}")
        else:
            matches = glob.glob(arg)
            if matches:
                targets.extend(matches)
            else:
                targets.append(arg)

    if not targets:
        print("⚠️  rm: missing operand")
        return

    # -I prompt (once for 3+ or recursive)
    if flags["-I"] and (len(targets) > 3 or flags["-r"]):
        confirm = input(f"rm: remove {len(targets)} items? [y/N]: ")
        if confirm.lower() != 'y':
            print("❌ Aborted.")
            return

    for path in targets:
        if not os.path.exists(path):
            if not flags["-f"]:
                print(f"⚠️  rm: cannot remove '{path}': No such file or directory")
            continue

        is_dir = os.path.isdir(path)

        # -i: ask before every removal
        if flags["-i"]:
            confirm = input(f"rm: remove {'directory' if is_dir else 'file'} '{path}'? [y/N]: ")
            if confirm.lower() != 'y':
                print("❌ Skipped.")
                continue

        try:
            if is_dir:
                if flags["-d"]:
                    if not os.listdir(path):
                        os.rmdir(path)
                        if flags["-v"]:
                            print(f"✔️ removed empty directory '{path}'")
                    elif not flags["-f"]:
                        print(f"⚠️  rm: cannot remove '{path}': Directory not empty")
                elif flags["-r"]:
                    shutil.rmtree(path)
                    if flags["-v"]:
                        print(f"✔️ recursively removed directory '{path}'")
                else:
                    print(f"⚠️  rm: cannot remove '{path}': Is a directory")
            else:
                os.remove(path)
                if flags["-v"]:
                    print(f"✔️ removed file '{path}'")
        except Exception as e:
            if not flags["-f"]:
                print(f"❌ rm: failed to remove '{path}': {e}")

#cp
def cp_command(raw_input):
    import os, shutil, shlex
    from pathlib import Path

    args = shlex.split(raw_input)[1:]
    flags = {
        "archive": False, "backup": False, "force": False,
        "interactive": False, "link": False, "no_clobber": False,
        "recursive": False, "suffix": "~", "target_dir": None
    }

    sources = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-a", "--archive"): flags["archive"] = flags["recursive"] = True
        elif arg in ("-b", "--backup"): flags["backup"] = True
        elif arg in ("-f", "--force"): flags["force"] = True
        elif arg in ("-i", "--interactive"): flags["interactive"] = True
        elif arg in ("-l", "--link"): flags["link"] = True
        elif arg in ("-n", "--no-clobber"): flags["no_clobber"] = True
        elif arg in ("-r", "-R", "--recursive"): flags["recursive"] = True
        elif arg.startswith("--suffix="): flags["suffix"] = arg.split("=", 1)[1]
        elif arg == "-S": i += 1; flags["suffix"] = args[i]
        elif arg.startswith("--target-directory="): flags["target_dir"] = arg.split("=", 1)[1]
        elif arg == "-t": i += 1; flags["target_dir"] = args[i]
        else: sources.append(arg)
        i += 1

    if not sources:
        print("⚠️  cp: missing file operand")
        return

    def copy(src_path: Path, dest_path: Path):
        if not src_path.exists():
            print(f"⚠️  cp: cannot stat '{src_path}': No such file or directory")
            return

        dest_exists = dest_path.exists()

        # Overwrite protection logic
        if dest_exists:
            if flags["no_clobber"]:
                print(f"ℹ️  cp: not overwriting '{dest_path}' (no-clobber)")
                return
            if flags["interactive"]:
                ans = input(f"cp: overwrite '{dest_path}'? [y/N]: ")
                if ans.lower() != "y":
                    print("❌ Skipped.")
                    return
            if flags["backup"]:
                backup_path = dest_path.with_name(dest_path.name + flags["suffix"])
                shutil.copy2(dest_path, backup_path)
                print(f"🔁 Backup created: {backup_path}")

        try:
            if flags["link"]:
                os.link(src_path, dest_path)
            elif src_path.is_dir():
                if not flags["recursive"]:
                    print(f"⚠️  cp: omitting directory '{src_path}' (use -r)")
                    return
                shutil.copytree(
                    src_path, dest_path,
                    copy_function=shutil.copy2 if flags["archive"] else shutil.copy,
                    dirs_exist_ok=flags["force"]
                )
            else:
                shutil.copy2(src_path, dest_path) if flags["archive"] else shutil.copy(src_path, dest_path)
            print(f"✅ Copied '{src_path}' → '{dest_path}'")
        except Exception as e:
            print(f"❌ cp: failed to copy '{src_path}' → '{dest_path}': {e}")

    # Handle target directory flag
    if flags["target_dir"]:
        target_dir = Path(flags["target_dir"])
        if not target_dir.is_dir():
            print(f"⚠️  cp: target directory '{target_dir}' does not exist or is not a directory")
            return
        for src in sources:
            src_path = Path(src)
            copy(src_path, target_dir / src_path.name)
        return

    # Normal copy logic
    *src_list, dest_arg = sources
    dest = Path(dest_arg)

    if len(src_list) > 1 and not dest.is_dir():
        print("⚠️  cp: when copying multiple files, destination must be a directory")
        return

    for src in src_list:
        src_path = Path(src)
        dest_path = dest / src_path.name if dest.is_dir() else dest
        copy(src_path, dest_path)

#mv
def mv_command(raw_input):
    import os, shutil, shlex
    from pathlib import Path

    args = shlex.split(raw_input)[1:]  # remove 'mv'

    flags = {
        "force": False, "interactive": False, "no_clobber": False,
        "verbose": False, "backup": False, "suffix": "~", "target_dir": None
    }

    sources = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-f", "--force"): flags["force"] = True
        elif arg in ("-i", "--interactive"): flags["interactive"] = True
        elif arg in ("-n", "--no-clobber"): flags["no_clobber"] = True
        elif arg in ("-v", "--verbose"): flags["verbose"] = True
        elif arg in ("-b", "--backup"): flags["backup"] = True
        elif arg.startswith("--suffix="): flags["suffix"] = arg.split("=", 1)[1]
        elif arg.startswith("--target-directory="): flags["target_dir"] = arg.split("=", 1)[1]
        elif arg == "-t": i += 1; flags["target_dir"] = args[i]
        elif arg == "--": i += 1; break
        else: sources.append(arg)
        i += 1

    sources += args[i:]

    if not sources:
        print("⚠️  mv: missing file operand")
        return

    def move(src_str, dest_str):
        src = Path(src_str).resolve()
        dest = Path(dest_str).resolve()
        if not src.exists():
            print(f"⚠️  mv: cannot stat '{src}': No such file or directory")
            return

        if dest.exists():
            if flags["no_clobber"]:
                if flags["verbose"]:
                    print(f"ℹ️  mv: not overwriting '{dest}' (no-clobber)")
                return
            if flags["interactive"]:
                ans = input(f"mv: overwrite '{dest}'? [y/N]: ")
                if ans.lower() != "y":
                    print("❌ Skipped.")
                    return
            if flags["backup"]:
                backup = dest.with_name(dest.name + flags["suffix"])
                try:
                    shutil.copy2(dest, backup)
                    if flags["verbose"]:
                        print(f"🔁 Backup: '{backup}'")
                except Exception as e:
                    print(f"❌ mv: backup failed: {e}")
                    return

        try:
            shutil.move(str(src), str(dest))
            if flags["verbose"]:
                print(f"✅ Moved '{src}' → '{dest}'")
        except Exception as e:
            print(f"❌ mv: failed to move '{src}' → '{dest}': {e}")

    # Handle -t/--target-directory
    if flags["target_dir"]:
        target_dir = Path(flags["target_dir"]).resolve()
        if not target_dir.is_dir():
            print(f"⚠️  mv: target directory '{target_dir}' does not exist")
            return
        for src in sources:
            src_path = Path(src).resolve()
            move(src_path, target_dir / src_path.name)
        return

    # Normal move (last is destination)
    *src_list, dest_arg = sources
    dest = Path(dest_arg).resolve()

    if len(src_list) > 1 and not dest.is_dir():
        print("⚠️  mv: target must be a directory when moving multiple files")
        return

    for src in src_list:
        src_path = Path(src).resolve()
        dest_path = dest / src_path.name if dest.is_dir() else dest
        move(src_path, dest_path)

#head
def head_command(raw_input):
    import shlex
    args = shlex.split(raw_input)[1:]  # remove 'head'

    count = 10
    files = []

    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-n", "--lines"):
            i += 1
            count = int(args[i])
        else:
            files.append(arg)
        i += 1

    if not files:
        print("⚠️  head: missing file operand")
        return

    for file in files:
        try:
            with open(file, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
                print(f"\n==> {file} <==" if len(files) > 1 else "")
                print("".join(lines[:count]), end="")
        except Exception as e:
            print(f"❌ head: {file}: {e}")

#tail
def tail_command(raw_input):
    import shlex
    args = shlex.split(raw_input)[1:]  # remove 'tail'

    count = 10
    files = []

    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-n", "--lines"):
            i += 1
            count = int(args[i])
        else:
            files.append(arg)
        i += 1

    if not files:
        print("⚠️  tail: missing file operand")
        return

    for file in files:
        try:
            with open(file, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
                print(f"\n==> {file} <==" if len(files) > 1 else "")
                print("".join(lines[-count:]), end="")
        except Exception as e:
            print(f"❌ tail: {file}: {e}")
