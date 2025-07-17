import os, sys, shutil, shlex, glob, threading, unicodedata
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

#locate
def locate_command(raw_input):
    import os, shlex, re
    from pathlib import Path

    args = shlex.split(raw_input)[1:]  # remove 'locate'

    # Flags
    flags = {
        "null": False, "all": False, "basename": False,
        "count": False, "existing": False, "ignore_case": False,
        "limit": None, "ignore_spaces": False, "quiet": False,
        "statistics": False, "transliterate": False,
        "database": None, "patterns": []
    }

    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-0", "--null"): flags["null"] = True
        elif arg in ("-A", "--all"): flags["all"] = True
        elif arg in ("-b", "--basename"): flags["basename"] = True
        elif arg in ("-c", "--count"): flags["count"] = True
        elif arg in ("-e", "--existing"): flags["existing"] = True
        elif arg in ("-i", "--ignore-case"): flags["ignore_case"] = True
        elif arg in ("-l", "--limit", "-n"): i += 1; flags["limit"] = int(args[i])
        elif arg in ("-p", "--ignore-spaces"): flags["ignore_spaces"] = True
        elif arg in ("-q", "--quiet"): flags["quiet"] = True
        elif arg in ("-S", "--statistics"): flags["statistics"] = True
        elif arg in ("-t", "--transliterate"): flags["transliterate"] = True
        elif arg in ("-w", "--wholename"): flags["basename"] = False
        elif arg in ("-d", "--database"): i += 1; flags["database"] = args[i]
        else: flags["patterns"].append(arg)
        i += 1

    def load_db():
        entries = []
        if flags["database"]:
            for path in flags["database"].split(":"):
                try:
                    with open(path.strip(), "r", encoding="utf-8", errors="ignore") as f:
                        entries.extend(line.strip() for line in f if line.strip())
                except Exception as e:
                    if not flags["quiet"]:
                        print(f"⚠️  locate: cannot read database '{path}': {e}")
        else:
            for root, _, files in os.walk("."):
                for f in files:
                    entries.append(os.path.join(root, f))
        return entries

    def normalize(text):
        if flags["transliterate"]:
            trans = str.maketrans("áéíóúÁÉÍÓÚ", "aeiouAEIOU")
            text = text.translate(trans)
        if flags["ignore_spaces"]:
            text = re.sub(r'[\s\W_]+', '', text)
        return text

    def is_match(path, patterns):
        target = os.path.basename(path) if flags["basename"] else path
        target = normalize(target)

        if flags["ignore_case"]:
            matches = [(normalize(p).lower() in target.lower()) for p in patterns]
        else:
            matches = [(normalize(p) in target) for p in patterns]

        return all(matches) if flags["all"] else any(matches)

    try:
        db = load_db()

        if flags["statistics"]:
            size = sum(len(e.encode()) + 1 for e in db)
            print(f"Paths: {len(db)}\nSize: {size} bytes")
            return

        results = []
        for path in db:
            if flags["existing"] and not os.path.exists(path):
                continue
            if is_match(path, flags["patterns"]):
                results.append(path)

        if flags["count"]:
            print(len(results))
        else:
            output = results[:flags["limit"]] if flags["limit"] else results
            sep = '\0' if flags["null"] else '\n'
            print(sep.join(output))

    except Exception as e:
        if not flags["quiet"]:
            print(f"❌ locate: {e}")

#find
def find_command(raw_input):
    import os, shlex, stat, pwd, grp
    from pathlib import Path
    from datetime import datetime

    args = shlex.split(raw_input)[1:]  # remove 'find'

    # Defaults
    start = "."
    options = {
        "name": None, "iname": None, "type": None,
        "empty": False, "user": None, "group": None,
        "perm": None, "size": None,
        "ctime": None, "mtime": None, "atime": None,
        "mindepth": 0, "maxdepth": float("inf"),
        "not": False, "prune": False, "print": False,
        "exec": None, "follow": "P"
    }

    # Parse args
    i = 0
    while i < len(args):
        arg = args[i]
        if not arg.startswith("-") and i == 0: start = arg
        elif arg == "-name": i += 1; options["name"] = args[i]
        elif arg == "-iname": i += 1; options["iname"] = args[i].lower()
        elif arg == "-type": i += 1; options["type"] = args[i]
        elif arg == "-empty": options["empty"] = True
        elif arg == "-user": i += 1; options["user"] = args[i]
        elif arg == "-group": i += 1; options["group"] = args[i]
        elif arg == "-perm": i += 1; options["perm"] = int(args[i], 8)
        elif arg == "-size": i += 1; options["size"] = args[i]
        elif arg == "-ctime": i += 1; options["ctime"] = int(args[i])
        elif arg == "-mtime": i += 1; options["mtime"] = int(args[i])
        elif arg == "-atime": i += 1; options["atime"] = int(args[i])
        elif arg == "-mindepth": i += 1; options["mindepth"] = int(args[i])
        elif arg == "-maxdepth": i += 1; options["maxdepth"] = int(args[i])
        elif arg == "-not": options["not"] = True
        elif arg == "-prune": options["prune"] = True
        elif arg == "-print": options["print"] = True
        elif arg == "-exec": i += 1; options["exec"] = args[i:]
        elif arg == "-L": options["follow"] = "L"
        elif arg == "-P": options["follow"] = "P"
        i += 1

    results = []

    def match(p: Path, st, depth):
        try:
            if depth < options["mindepth"]: return False
            if options["name"] and p.name != options["name"]: return False
            if options["iname"] and p.name.lower() != options["iname"]: return False
            if options["type"]:
                if options["type"] == "f" and not p.is_file(): return False
                if options["type"] == "d" and not p.is_dir(): return False
                if options["type"] == "l" and not p.is_symlink(): return False
            if options["empty"]:
                if p.is_file() and st.st_size != 0: return False
                if p.is_dir() and any(p.iterdir()): return False
            if options["user"]:
                uid = st.st_uid
                uname = pwd.getpwuid(uid).pw_name if not options["user"].isdigit() else uid
                if uname != options["user"] and uid != int(options["user"]): return False
            if options["group"]:
                gid = st.st_gid
                gname = grp.getgrgid(gid).gr_name if not options["group"].isdigit() else gid
                if gname != options["group"] and gid != int(options["group"]): return False
            if options["perm"] is not None:
                if stat.S_IMODE(st.st_mode) != options["perm"]: return False
            if options["size"]:
                suffix = options["size"][-1]
                val = int(options["size"][:-1])
                fsz = st.st_size
                if suffix == "c" and fsz != val: return False
                if suffix == "k" and fsz // 1024 != val: return False
            for key in ("ctime", "mtime", "atime"):
                if options[key] is not None:
                    delta = datetime.now() - datetime.fromtimestamp(getattr(st, f"st_{key}"))
                    if delta.days != options[key]: return False
            return True
        except Exception:
            return False

    def walk(current: Path, depth=0):
        if depth > options["maxdepth"]: return
        try:
            for entry in os.scandir(current):
                p = Path(entry.path)
                st = entry.stat(follow_symlinks=(options["follow"] == "L"))
                matched = match(p, st, depth)
                if options["not"]: matched = not matched
                if matched:
                    results.append(str(p))
                    if options["exec"]:
                        cmd = " ".join(options["exec"]).replace("{}", str(p))
                        os.system(cmd)
                    if options["prune"]: continue
                if entry.is_dir(follow_symlinks=(options["follow"] == "L")):
                    walk(p, depth + 1)
        except Exception: pass

    walk(Path(start))

    if options["print"] or not options["exec"]:
        for r in results:
            print(r)

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

#locate
def locate_command(raw_input):
    args = shlex.split(raw_input)[1:]
    patterns = []
    flags = {
        "null": False,
        "all": False,
        "basename": False,
        "count": False,
        "database": "locate.db",
        "existing": False,
        "follow": False,
        "ignore_case": False,
        "limit": None,
        "ignore_spaces": False,
        "quiet": False,
        "statistics": False,
        "transliterate": False,
        "wholename": True  # default Linux behavior
    }

    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-0", "--null"):
            flags["null"] = True
        elif arg in ("-A", "--all"):
            flags["all"] = True
        elif arg in ("-b", "--basename"):
            flags["basename"] = True
            flags["wholename"] = False
        elif arg in ("-c", "--count"):
            flags["count"] = True
        elif arg in ("-d", "--database"):
            i += 1
            flags["database"] = args[i]
        elif arg in ("-e", "--existing"):
            flags["existing"] = True
        elif arg in ("-L", "--follow"):
            flags["follow"] = True
        elif arg in ("-i", "--ignore-case"):
            flags["ignore_case"] = True
        elif arg in ("-l", "--limit", "-n"):
            i += 1
            flags["limit"] = int(args[i])
        elif arg in ("-p", "--ignore-spaces"):
            flags["ignore_spaces"] = True
        elif arg in ("-q", "--quiet"):
            flags["quiet"] = True
        elif arg in ("-S", "--statistics"):
            flags["statistics"] = True
        elif arg in ("-t", "--transliterate"):
            flags["transliterate"] = True
        elif arg in ("-w", "--wholename"):
            flags["wholename"] = True
        else:
            patterns.append(arg)
        i += 1

    # Load DB
    try:
        with open(flags["database"], "r", encoding="utf-8") as db:
            entries = db.read().splitlines()
    except Exception as e:
        if not flags["quiet"]:
            print(f"❌ locate: failed to read database: {e}")
        return

    if flags["statistics"]:
        print(f"Database: {flags['database']}")
        print(f"Entries: {len(entries)}")
        return

    def normalize(s):
        s = unicodedata.normalize("NFKD", s) if flags["transliterate"] else s
        s = s.lower() if flags["ignore_case"] else s
        if flags["ignore_spaces"]:
            s = ''.join(c for c in s if c.isalnum())
        return s

    def match(entry, patterns):
        entry_cmp = normalize(os.path.basename(entry) if flags["basename"] else entry)
        if flags["all"]:
            return all(normalize(pat) in entry_cmp for pat in patterns)
        return any(normalize(pat) in entry_cmp for pat in patterns)

    matched = []
    for path in entries:
        if patterns and not match(path, patterns):
            continue
        if flags["existing"] and not os.path.exists(path):
            continue
        if flags["follow"] and os.path.islink(path) and not os.path.exists(os.readlink(path)):
            continue
        matched.append(path)
        if flags["limit"] and len(matched) >= flags["limit"]:
            break

    if flags["count"]:
        print(len(matched))
    else:
        sep = '\0' if flags["null"] else '\n'
        print(sep.join(matched), end=sep if matched else "")


#df

#du