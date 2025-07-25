import os, sys, shutil, shlex, glob, threading, subprocess, argparse, fnmatch
import stat
import time
import ctypes
from pathlib import Path
from datetime import datetime
from . import CLS_check

try:
    import grp
except:
    os.system("pip install grp")

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
def sudo_command():
    python = shutil.which("python")
    script = os.path.abspath(sys.argv[0])
    args = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])

    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", python, f'"{script}" {args}', None, 1
        )
        print("✅ New Admin Python terminal launched (UAC may prompt).")
    except Exception as e:
        print(f"❌ Failed to elevate: {e}")


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

#tree
def tree_command(raw_input):
    import os, shlex
    from pathlib import Path

    args = shlex.split(raw_input)
    path = Path(args[1]) if len(args) > 1 else Path(".")

    if not path.exists() or not path.is_dir():
        print(f"❌ tree: '{path}' is not a valid directory")
        return

    dir_count = file_count = 0

    def walk(dir_path: Path, prefix=""):
        nonlocal dir_count, file_count
        entries = sorted(list(dir_path.iterdir()))
        for idx, entry in enumerate(entries):
            connector = "└── " if idx == len(entries) - 1 else "├── "
            print(prefix + connector + entry.name)

            if entry.is_dir():
                dir_count += 1
                extension = "    " if idx == len(entries) - 1 else "│   "
                walk(entry, prefix + extension)
            else:
                file_count += 1

    print(f"{path.resolve().name}/")
    walk(path.resolve())
    print(f"\n📁 {dir_count} directories, 📄 {file_count} files")


#head
def head_command(raw_input):
    args = shlex.split(raw_input)[1:]  # remove 'head'
    files = []
    num_lines = 10
    num_bytes = None
    show_header = None  # None = auto, True = -v, False = -q

    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-n", "--lines"):
            i += 1
            num_lines = int(args[i])
        elif arg in ("-c", "--bytes"):
            i += 1
            num_bytes = int(args[i])
        elif arg in ("-v", "--verbose"):
            show_header = True
        elif arg in ("-q", "--quiet"):
            show_header = False
        elif arg.startswith("-") and arg[1:].isdigit():
            num_lines = int(arg[1:])  # support like `head -5`
        else:
            files.append(arg)
        i += 1

    if not files:
        print("⚠️  head: missing file operand")
        return

    for idx, file in enumerate(files):
        if not os.path.isfile(file):
            print(f"❌ head: cannot open '{file}' for reading")
            continue

        try:
            with open(file, "rb") as f:
                content = f.read()

            # Output header if needed
            if show_header is True or (show_header is None and len(files) > 1):
                print(f"==> {file} <==")

            # Output lines or bytes
            if num_bytes is not None:
                print(content[:num_bytes].decode("utf-8", errors="replace"), end="")
            else:
                lines = content.decode("utf-8", errors="replace").splitlines()
                print("\n".join(lines[:num_lines]))
            
            if idx < len(files) - 1 and show_header is not False:
                print()

        except Exception as e:
            print(f"❌ head: {file}: {e}")

#tail
def tail_command(raw_input):
    args = shlex.split(raw_input)[1:]
    files = []
    options = {
        "lines": 10,
        "bytes": None,
        "lines_from": None,
        "bytes_from": None,
        "follow": None,
        "retry": False,
        "pid": None,
        "sleep": 1,
        "verbose": False,
        "quiet": False,
        "zero": False,
        "max_unchanged_stats": 5
    }

    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-n", "--lines"):
            i += 1
            val = args[i]
            options["lines_from"] = int(val[1:]) if val.startswith("+") else None
            options["lines"] = int(val.lstrip("+"))
        elif arg in ("-c", "--bytes"):
            i += 1
            val = args[i]
            options["bytes_from"] = int(val[1:]) if val.startswith("+") else None
            options["bytes"] = int(val.lstrip("+"))
        elif arg.startswith("--pid="):
            options["pid"] = int(arg.split("=", 1)[1])
        elif arg.startswith("--max-unchanged-stats="):
            options["max_unchanged_stats"] = int(arg.split("=", 1)[1])
        elif arg.startswith("--sleep-interval=") or arg == "-s":
            if "=" in arg:
                options["sleep"] = float(arg.split("=", 1)[1])
            else:
                i += 1
                options["sleep"] = float(args[i])
        elif arg.startswith("--follow="):
            options["follow"] = arg.split("=", 1)[1]
        elif arg in ("-f", "--follow"):
            options["follow"] = "descriptor"
        elif arg == "-F":
            options["follow"] = "name"
            options["retry"] = True
        elif arg in ("-q", "--quiet", "--silent"):
            options["quiet"] = True
        elif arg in ("-v", "--verbose"):
            options["verbose"] = True
        elif arg in ("-z", "--zero-terminated"):
            options["zero"] = True
        else:
            files.append(arg)
        i += 1

    def is_pid_alive(pid):
        try:
            os.kill(pid, 0)
            return True
        except:
            return False

    def read_tail(file, print_header=True):
        sep = '\0' if options["zero"] else '\n'
        try:
            with open(file, "rb") as f:
                content = f.read()
                if options["bytes"] is not None:
                    if options["bytes_from"] is not None:
                        out = content[options["bytes_from"] - 1:]
                    else:
                        out = content[-options["bytes"]:]
                    print(out.decode("utf-8", errors="replace"), end="")
                else:
                    lines = content.decode("utf-8", errors="replace").splitlines()
                    if options["lines_from"] is not None:
                        out = lines[options["lines_from"] - 1:]
                    else:
                        out = lines[-options["lines"]:]
                    print(sep.join(out), end=sep if out else "")
        except Exception as e:
            print(f"❌ tail: cannot read '{file}': {e}")

    def follow_file(file):
        unchanged_count = 0
        prev_size = -1
        while True:
            if options["pid"] and not is_pid_alive(options["pid"]):
                break
            try:
                curr_size = os.path.getsize(file)
                if curr_size > prev_size:
                    with open(file, "rb") as f:
                        f.seek(prev_size if prev_size > 0 else 0)
                        data = f.read()
                        print(data.decode("utf-8", errors="replace"), end="")
                    prev_size = curr_size
                    unchanged_count = 0
                else:
                    unchanged_count += 1
                if unchanged_count >= options["max_unchanged_stats"]:
                    if options["retry"] and not os.path.exists(file):
                        print(f"\n🔁 Retrying {file}...")
                        while not os.path.exists(file):
                            time.sleep(options["sleep"])
                        prev_size = 0
                    unchanged_count = 0
                time.sleep(options["sleep"])
            except KeyboardInterrupt:
                break
            except Exception:
                time.sleep(options["sleep"])

    if not files:
        print("⚠️  tail: missing file operand")
        return

    for idx, file in enumerate(files):
        if not os.path.exists(file):
            print(f"❌ tail: {file}: No such file")
            continue
        if not options["quiet"] and (options["verbose"] or len(files) > 1):
            print(f"==> {file} <==")

        read_tail(file)

        if options["follow"]:
            t = threading.Thread(target=follow_file, args=(file,), daemon=True)
            t.start()
            t.join()

#find
def find_command(raw_input: str):
    import shlex
    args = shlex.split(raw_input)
    if len(args) < 2 or args[0] != "find":
        print("Usage: find <path> [options]")
        return

    start_path = args[1]
    filters = []
    exec_cmd = []
    follow_symlinks = False
    max_depth = None
    min_depth = 0
    negate = False
    default_action = True

    i = 2
    while i < len(args):
        token = args[i]

        if token == "-name" and i + 1 < len(args):
            filters.append(("name", args[i + 1], negate))
            i += 1
            negate = False

        elif token == "-iname" and i + 1 < len(args):
            filters.append(("iname", args[i + 1], negate))
            i += 1
            negate = False

        elif token == "-type" and i + 1 < len(args):
            filters.append(("type", args[i + 1], negate))
            i += 1
            negate = False

        elif token == "-empty":
            filters.append(("empty", None, negate))
            negate = False

        elif token == "-size" and i + 1 < len(args):
            size_str = args[i + 1]
            op = size_str[0] if size_str[0] in "+-=" else "="
            val = int(size_str.lstrip("+-="))
            filters.append(("size", (op, val), negate))
            i += 1
            negate = False

        elif token == "-perm" and i + 1 < len(args):
            perm = int(args[i + 1], 8)
            filters.append(("perm", perm, negate))
            i += 1
            negate = False

        elif token == "-user" and i + 1 < len(args):
            filters.append(("user", args[i + 1], negate))
            i += 1
            negate = False

        elif token == "-group" and i + 1 < len(args):
            filters.append(("group", args[i + 1], negate))
            i += 1
            negate = False

        elif token == "-mtime" and i + 1 < len(args):
            filters.append(("mtime", int(args[i + 1]), negate))
            i += 1
            negate = False

        elif token == "-atime" and i + 1 < len(args):
            filters.append(("atime", int(args[i + 1]), negate))
            i += 1
            negate = False

        elif token == "-ctime" and i + 1 < len(args):
            filters.append(("ctime", int(args[i + 1]), negate))
            i += 1
            negate = False

        elif token == "-mindepth" and i + 1 < len(args):
            min_depth = int(args[i + 1])
            i += 1

        elif token == "-maxdepth" and i + 1 < len(args):
            max_depth = int(args[i + 1])
            i += 1

        elif token == "-L":
            follow_symlinks = True

        elif token == "-P":
            follow_symlinks = False

        elif token == "-not":
            negate = True

        elif token == "-exec":
            i += 1
            while i < len(args) and args[i] != ";":
                exec_cmd.append(args[i])
                i += 1
            default_action = False

        elif token == "-print":
            default_action = True

        i += 1

    abs_start = os.path.abspath(start_path)

    def match_filters(path, entry):
        try:
            st = os.stat(path, follow_symlinks=follow_symlinks)
        except Exception:
            return False

        for key, value, is_not in filters:
            result = False
            if key == "name":
                result = fnmatch.fnmatch(entry, value)
            elif key == "iname":
                result = fnmatch.fnmatch(entry.lower(), value.lower())
            elif key == "type":
                if value == "f":
                    result = os.path.isfile(path)
                elif value == "d":
                    result = os.path.isdir(path)
                elif value == "l":
                    result = os.path.islink(path)
            elif key == "empty":
                if os.path.isfile(path):
                    result = os.path.getsize(path) == 0
                elif os.path.isdir(path):
                    result = len(os.listdir(path)) == 0
            elif key == "size":
                size = os.path.getsize(path)
                op, val = value
                if op == "+":
                    result = size > val
                elif op == "-":
                    result = size < val
                else:
                    result = size == val
            elif key == "perm":
                result = stat.S_IMODE(st.st_mode) == value
            elif key == "user":
                try:
                    result = os.getlogin() == value
                except:
                    result = False
            elif key == "group":
                result = False  # Not supported on Windows
            elif key == "mtime":
                result = (time.time() - st.st_mtime) // 86400 == value
            elif key == "atime":
                result = (time.time() - st.st_atime) // 86400 == value
            elif key == "ctime":
                result = (time.time() - st.st_ctime) // 86400 == value

            if is_not:
                result = not result
            if not result:
                return False
        return True

    for root, dirs, files in os.walk(start_path, followlinks=follow_symlinks):
        depth = os.path.abspath(root).count(os.sep) - abs_start.count(os.sep)
        if max_depth is not None and depth > max_depth:
            continue
        if depth < min_depth:
            continue

        for entry in dirs + files:
            path = os.path.join(root, entry)
            if match_filters(path, entry):
                if exec_cmd:
                    cmd = [p if p != "{}" else path for p in exec_cmd]
                    try:
                        subprocess.run(cmd)
                    except Exception as e:
                        print(f"[exec error] {e}")
                elif default_action:
                    print(path)

#df
def df_command(raw_input):
    import os, shutil, shlex
    from collections import namedtuple

    args = shlex.split(raw_input)
    args = args[1:]  # Remove "df"

    # Default options
    flags = {
        "human": False,
        "total": False,
        "print_type": False,
        "all": False,
        "only_type": None,
        "exclude_type": None
    }

    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ["-h", "--human-readable"]:
            flags["human"] = True
        elif arg == "--total":
            flags["total"] = True
        elif arg in ["-T", "--print-type"]:
            flags["print_type"] = True
        elif arg in ["-a", "--all"]:
            flags["all"] = True
        elif arg.startswith("-x") or arg.startswith("--exclude-type="):
            val = arg.split("=")[-1] if "=" in arg else args[i+1]
            flags["exclude_type"] = val.upper()
            if "=" not in arg:
                i += 1
        elif arg.startswith("-t") or arg.startswith("--type="):
            val = arg.split("=")[-1] if "=" in arg else args[i+1]
            flags["only_type"] = val.upper()
            if "=" not in arg:
                i += 1
        i += 1

    def humanize(size):
        for unit in ['B', 'K', 'M', 'G', 'T']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}P"

    print(f"{'Filesystem':<20} {'Type':<8} {'Size':>10} {'Used':>10} {'Avail':>10} {'Use%':>6} {'Mounted on'}")

    total_size = total_used = total_free = 0
    drives = [f"{chr(d)}:\\" for d in range(65, 91) if os.path.exists(f"{chr(d)}:\\")]

    for drive in drives:
        try:
            # Simulate filesystem type
            fs_type = "NTFS"  # Could use `pywin32` or `psutil` to get real FS type
            if flags["exclude_type"] and fs_type == flags["exclude_type"]:
                continue
            if flags["only_type"] and fs_type != flags["only_type"]:
                continue

            usage = shutil.disk_usage(drive)
            size, used, free = usage.total, usage.used, usage.free
            percent = f"{(used * 100) // size}%"
            total_size += size
            total_used += used
            total_free += free

            size_str = humanize(size) if flags["human"] else str(size)
            used_str = humanize(used) if flags["human"] else str(used)
            free_str = humanize(free) if flags["human"] else str(free)
            fs_str = fs_type if flags["print_type"] else ""

            print(f"{drive:<20} {fs_str:<8} {size_str:>10} {used_str:>10} {free_str:>10} {percent:>6} {drive}")
        except Exception as e:
            print(f"⚠️  Error reading {drive}: {e}")

    if flags["total"]:
        size_str = humanize(total_size) if flags["human"] else str(total_size)
        used_str = humanize(total_used) if flags["human"] else str(total_used)
        free_str = humanize(total_free) if flags["human"] else str(total_free)
        percent = f"{(total_used * 100) // total_size}%" if total_size else "0%"
        print(f"{'total':<20} {'':<8} {size_str:>10} {used_str:>10} {free_str:>10} {percent:>6} -")

#du
def du_command(raw_input):
    import os, shlex
    from pathlib import Path

    args = shlex.split(raw_input)
    args = args[1:]  # Remove 'du'

    flags = {
        "all": False,
        "human": False,
        "summarize": False,
        "total": False,
        "max_depth": None,
        "threshold": 0
    }

    paths = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ["-a", "--all"]:
            flags["all"] = True
        elif arg in ["-h", "--human-readable"]:
            flags["human"] = True
        elif arg in ["-s", "--summarize"]:
            flags["summarize"] = True
        elif arg in ["-c", "--total"]:
            flags["total"] = True
        elif arg.startswith("-d") or arg.startswith("--max-depth="):
            if "=" in arg:
                flags["max_depth"] = int(arg.split("=")[1])
            else:
                i += 1
                flags["max_depth"] = int(args[i])
        elif arg.startswith("-t") or arg.startswith("--threshold="):
            if "=" in arg:
                flags["threshold"] = int(arg.split("=")[1])
            else:
                i += 1
                flags["threshold"] = int(args[i])
        else:
            paths.append(arg)
        i += 1

    if not paths:
        paths = ["."]

    def humanize(size):
        for unit in ['B', 'K', 'M', 'G', 'T']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}P"

    def get_size(path, level=0, base_level=0):
        total = 0
        try:
            if path.is_file():
                size = path.stat().st_size
                if flags["all"] and size >= flags["threshold"] * 1024:
                    print(f"{humanize(size) if flags['human'] else size}\t{path}")
                return size

            for item in path.iterdir():
                if item.is_symlink():
                    continue
                item_size = get_size(item, level + 1, base_level)
                total += item_size

            if not flags["summarize"] and (flags["max_depth"] is None or level - base_level <= flags["max_depth"]):
                if total >= flags["threshold"] * 1024:
                    print(f"{humanize(total) if flags['human'] else total}\t{path}")
            return total
        except Exception as e:
            print(f"⚠️  du: {path}: {e}")
            return 0

    grand_total = 0
    for path_str in paths:
        path = Path(path_str)
        if not path.exists():
            print(f"⚠️  du: cannot access '{path}': No such file or directory")
            continue
        base_level = len(path.resolve().parts)
        size = get_size(path, base_level, base_level)
        if flags["summarize"]:
            if size >= flags["threshold"] * 1024:
                print(f"{humanize(size) if flags['human'] else size}\t{path}")
        grand_total += size

    if flags["total"]:
        print(f"{humanize(grand_total) if flags['human'] else grand_total}\ttotal")

