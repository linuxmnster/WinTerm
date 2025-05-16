import os
import stat
import shutil
import time
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
def rmdir_command(cmd):
    # Step 1: Parse the command and arguments
    raw_args = cmd[len("rmdir"):].strip()
    args = []
    current = ''
    in_quotes = False
    force = False

    # Parse each character to handle spaces and quotes correctly
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

    # Check if the '-f' flag is in the arguments
    if "-f" in args:
        force = True
        args.remove("-f")  # Remove the flag so only folder names remain

    # Step 2: Handle no folder provided
    if not args:
        print("⚠️  rmdir: missing operand")
        return

    # Step 3: Process each folder
    for folder in args:
        try:
            # Check if the folder exists
            if not os.path.exists(folder):
                print(f"Error: No such directory: '{folder}'")
                continue
            
            # Step 4: Handle force flag for non-empty directories
            if force:
                if os.path.isdir(folder):
                    # Try to remove the directory forcefully
                    shutil.rmtree(folder)  # Force delete non-empty directory
                    print(f"📁 Deleted (force): {folder}")
                else:
                    print(f"Error: '{folder}' is not a directory")
            else:
                # Remove the folder only if it's empty
                if os.path.isdir(folder) and not os.listdir(folder):  # Check if empty
                    os.rmdir(folder)
                    print(f"📁 Deleted: {folder}")
                else:
                    print(f"Error: Directory '{folder}' is not empty. Use '-f' to force delete.")
                    
        except PermissionError:
            print(f"⚠️ Error: Permission denied: '{folder}'")
            # Retry logic: Attempt to delete again after a delay
            print(f"Attempting to retry after a short delay...")
            time.sleep(2)  # Wait for a brief moment before retrying
            try:
                shutil.rmtree(folder)  # Retry the deletion forcefully
                print(f"📁 Deleted (force): {folder}")
            except Exception as e:
                print(f"⚠️ Error: Failed to delete folder after retry: {e}")
                
        except Exception as e:
            print(f"⚠️ Error: {e}")