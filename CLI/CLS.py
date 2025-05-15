import os
import stat
import time
from CLS

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
def ls_command(input_command):
    # Get the current directory
    current_dir = os.getcwd()

    # Remove extra spaces and split by space
    command_parts = input_command.strip().split()

    # Check if flags are passed
    flags = command_parts[1:] if len(command_parts) > 1 else []

    # Get all files and directories
    try:
        files = os.listdir(current_dir)
    except FileNotFoundError:
        print("Directory not found.")
        return

    # If '-a' flag is not set, exclude hidden files
    if '-a' not in flags:
        files = [f for f in files if not f.startswith('.')]

    # If '-l' flag is set, show details
    if '-l' in flags:
        for file in files:
            file_path = os.path.join(current_dir, file)
            try:
                stats = os.stat(file_path)
                permissions = oct(stats.st_mode)[-3:]
                size = stats.st_size
                mtime = time.ctime(stats.st_mtime)

                # Colorize file names
                if stat.S_ISDIR(stats.st_mode):  # Check if it's a directory
                    file = colorize(file, "blue", None, None)  # Color directories blue
                else:
                    file = colorize(file, "green", None, None)  # Color regular files green

                print(f"{permissions} {size} {mtime} {file}")
            except Exception:
                print(f"Error with file {file}")
    else:
        # If no '-l', just print file names
        for file in files:
            # Colorize file names
            file_path = os.path.join(current_dir, file)
            try:
                stats = os.stat(file_path)
                if stat.S_ISDIR(stats.st_mode):
                    file = colorize(file, "blue", None, None)  # Color directories blue
                else:
                    file = colorize(file, "green", None, None)  # Color regular files green
                print(file)
            except Exception:
                print(f"Error with file {file}")
    
