import os
import stat
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
        files = os.listdir()
        if not show_all:
            files = [f for f in files if not f.startswith('.')]

        files.sort(key=lambda f: os.path.getmtime(f) if sort_time else f.lower(), reverse=reverse)

        if show_long:
            for f in files:
                path = os.path.join(os.getcwd(), f)
                stat_info = os.stat(path)
                is_dir = os.path.isdir(path)

                name = f"📁 {f}" if is_dir else f"📄 {f}"
                name = CLS_check.colorize(name, "blue", None, "bold") if is_dir else CLS_check.colorize(name, "white", None)

                perms = stat.filemode(stat_info.st_mode)
                size = stat_info.st_size
                if human:
                    for unit in ['B','K','M','G','T']:
                        if size < 1024:
                            break
                        size /= 1024
                    size = f"{size:.1f}{unit}"
                mtime = time.strftime('%b %d %H:%M', time.localtime(stat_info.st_mtime))
                print(f"{perms} {size:>6} {mtime} {name}")
        else:
            output = []
            for f in files:
                path = os.path.join(os.getcwd(), f)
                is_dir = os.path.isdir(path)
                name = f"📁 {f}" if is_dir else f"📄 {f}"
                name = CLS_check.colorize(name, "blue", None, "bold") if is_dir else CLS_check.colorize(name, "white", None)
                output.append(name)
            print('\t'.join(output))

    except Exception as e:
        print("Error:", e)
