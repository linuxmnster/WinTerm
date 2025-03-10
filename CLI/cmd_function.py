import os
import shutil
import zipfile
import subprocess
import psutil
import signal
import platform

#list_command
def list_visible_contents():
    """Lists only visible files and directories in the current working directory."""
    cwd = os.getcwd()
    items = [item for item in os.listdir(cwd) if not item.startswith('.')]  # Exclude hidden files

    directories = [item for item in items if os.path.isdir(os.path.join(cwd, item))]
    files = [item for item in items if os.path.isfile(os.path.join(cwd, item))]

    print("Directories:")
    for directory in directories:
        print(f"  📁 {directory}")

    print("\nFiles:")
    for file in files:
        print(f"  📄 {file}")

def list_all_contents():
    """Lists both hidden and non-hidden files and directories in the current working directory."""
    cwd = os.getcwd()
    items = os.listdir(cwd)  # List all items, including hidden ones

    print("Contents (Including Hidden Files):")
    for item in items:
        if item.startswith('.'):
            print(f"  🔴 .{item}")  # Indicate hidden files with a red dot emoji
        else:
            print(f"  📄 {item}" if os.path.isfile(os.path.join(cwd, item)) else f"  📁 {item}")

def tree(directory=None, prefix="", show_hidden=False):
    """Recursively prints the directory structure in a tree format."""
    if directory is None:
        directory = os.getcwd()
    try:
        items = sorted(os.listdir(directory))
        if not show_hidden:
            items = [item for item in items if not item.startswith(".")]

        num_items = len(items)
    except PermissionError:
        print(prefix + "└── [Permission Denied]")
        return

    for index, item in enumerate(items):
        path = os.path.join(directory, item)
        is_last = index == num_items - 1 

        branch = "└── " if is_last else "├── "

        print(prefix + branch + item)

        if os.path.isdir(path):
            new_prefix = prefix + ("    " if is_last else "│   ")
            tree(path, new_prefix, show_hidden)

def pwd():
    """Prints the current working directory."""
    print(os.getcwd())

#mkdir
def mkdir(*folders):
    """
    Creates one or multiple directories.

    - `mkdir <folder_name>`        → Creates a single folder in the current directory.
    - `mkdir <folder1> <folder2>`  → Creates multiple folders in the current directory.
    - `mkdir /path/to/folder`      → Creates a folder at a specified path.
    
    If a folder already exists, it skips creation and notifies the user.
    """
    if not folders:
        print("Error: No folder name provided.")
        return

    for folder in folders:
        try:
            os.makedirs(folder, exist_ok=False)  # Create directory (including parents if needed)
            print(f"Created: {os.path.abspath(folder)}")
        except PermissionError:
            print(f"Error: Permission denied for '{folder}'")
        except Exception as e:
            print(f"Error: {e}")

#change_directory
def cd(path=None):
    try:
        if path is None or path == "-":
            # Change to home directory
            new_path = os.path.expanduser("~")
        elif path == "..":
            # Move up one directory
            new_path = os.path.dirname(os.getcwd())
        elif path.startswith("../"):
            # Move up multiple levels (e.g., "../.." moves up two levels)
            new_path = os.path.abspath(os.path.join(os.getcwd(), path))
        elif path == "/":
            # Change to root directory
            new_path = "/"
        else:
            # Change to a specified directory
            new_path = os.path.abspath(path)

        os.chdir(new_path)  # Change the directory
        print(f"Changed directory to: {os.getcwd()}")

    except FileNotFoundError:
        print(f"Error: No such file or directory: '{path}'")
    except PermissionError:
        print(f"Error: Permission denied: '{path}'")
    except Exception as e:
        print(f"Error: {e}")

#rmdir
def rmdir(folder, force=False):
    """
    Removes an empty directory. If `-f` is used, removes non-empty directories.

    - `rmdir <folder>`     → Removes an empty folder.
    - `rmdir <folder> -f`  → Removes a folder and its contents (force delete).
    
    If the folder does not exist, an error is displayed.
    """
    try:
        if not os.path.exists(folder):
            print(f"Error: No such directory: '{folder}'")
            return

        if force:
            shutil.rmtree(folder)  # Force delete (removes non-empty folders)
            print(f"Deleted (force): {folder}")
        else:
            os.rmdir(folder)  # Removes only if empty
            print(f"Deleted: {folder}")

    except OSError:
        print(f"Error: Directory '{folder}' is not empty. Use '-f' to force delete.")
    except PermissionError:
        print(f"Error: Permission denied: '{folder}'")
    except Exception as e:
        print(f"Error: {e}")

#rm
def rm(file_path, force=False):
    """
    Removes a file.

    - `rm <file>`     → Deletes the specified file.
    - `rm <file> -f`  → Forces deletion without prompting.

    If the file does not exist, an error is displayed.
    """
    try:
        if not os.path.exists(file_path):
            print(f"Error: No such file: '{file_path}'")
            return

        if not os.path.isfile(file_path):
            print(f"Error: '{file_path}' is not a file.")
            return

        os.remove(file_path)
        print(f"Deleted: {file_path}")

    except PermissionError:
        print(f"Error: Permission denied: '{file_path}'")
    except Exception as e:
        print(f"Error: {e}")

def cp(source, destination):
    """
    Copies a file or directory.

    - `cp <source> <destination>` → Copies a file to a new location.
    - `cp <source> <dir/>` → Copies a file into a directory.
    - `cp -r <source_dir> <destination>` → Recursively copies a directory.

    If the source does not exist, an error is displayed.
    """
    try:
        if not os.path.exists(source):
            print(f"Error: Source '{source}' does not exist.")
            return

        if os.path.isdir(source):
            shutil.copytree(source, destination)  # Copy entire directory
            print(f"Copied directory: '{source}' → '{destination}'")
        else:
            shutil.copy2(source, destination)  # Copy file with metadata
            print(f"Copied file: '{source}' → '{destination}'")

    except FileExistsError:
        print(f"Error: Destination '{destination}' already exists.")
    except PermissionError:
        print(f"Error: Permission denied.")
    except Exception as e:
        print(f"Error: {e}")

#mv
def mv(source, destination):
    """
    Moves or renames a file/directory.

    - `mv <source> <destination>` → Moves or renames a file/directory.
    - `mv <file> <dir/>` → Moves a file into a directory.
    - `mv <old_name> <new_name>` → Renames a file or directory.

    If the source does not exist, an error is displayed.
    """
    try:
        if not os.path.exists(source):
            print(f"Error: Source '{source}' does not exist.")
            return

        shutil.move(source, destination)  # Move or rename
        print(f"Moved/Renamed: '{source}' → '{destination}'")

    except PermissionError:
        print(f"Error: Permission denied.")
    except Exception as e:
        print(f"Error: {e}")

def touch(filename):
    """
    Creates one or multiple files.

    - `touch <file>` → Creates a single file.
    - `touch <file1> <file2>` → Creates multiple files.
    - `touch /path/to/file` → Creates a file at a specific path.

    If the file exists, it updates the timestamp (like touch in Linux).
    """
    if not filename:
        print("Error: No file name provided.")
        return

    
    try:
        with open(filename, 'w') as file:
            pass  # Creates an empty file
        print(f"File '{filename}' Created")
    except Exception as e:
        print(f"Error: {e}")

        # try:
        #     os.makedirs(os.path.dirname(file), exist_ok=True)  # Ensure directory exists
        #     with open(file, 'a'):
        #         os.utime(file, None)  # Update timestamp or create file
        #     print(f"Created/Updated: {os.path.abspath(file)}")
        # except Exception as e:
        #     print(f"Error: {e}")


def unzip_file(zip_path, extract_to=None):
    """
    Unzips a ZIP file to a specified directory.
    
    :param zip_path: Path to the ZIP file.
    :param extract_to: Directory to extract files to. If None, extracts to the same directory as the ZIP file.
    """
    if not os.path.exists(zip_path):
        print("Error: ZIP file not found.")
        return

    if extract_to is None:
        extract_to = os.path.dirname(zip_path)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
            print(f"Successfully extracted to: {extract_to}")
    except zipfile.BadZipFile:
        print("Error: Not a valid ZIP file.")

def zip_files(output_filename, *sources):
    """
    Compresses files or directories into a ZIP archive.

    - `zip_files("archive.zip", "file1.txt", "file2.txt")` → Zips multiple files.
    - `zip_files("archive.zip", "folder/")` → Zips a folder and its contents.
    - `zip_files("archive.zip", "file1.txt", "folder/")` → Zips both files and folders.

    If the ZIP file already exists, it will be overwritten.
    """
    if not sources:
        print("Error: No files or directories specified to zip.")
        return

    try:
        with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
            for source in sources:
                if os.path.isdir(source):
                    # Add directory recursively
                    for root, _, files in os.walk(source):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zipf.write(file_path, os.path.relpath(file_path, os.path.dirname(source)))
                elif os.path.isfile(source):
                    zipf.write(source, os.path.basename(source))
                else:
                    print(f"Warning: {source} not found, skipping.")

        print(f"Created ZIP archive: {output_filename}")

    except Exception as e:
        print(f"Error: {e}")

def cat(filename):
    """
    Mimics the Linux 'cat' command by displaying the contents of a file.
    
    :param filename: Path to the file to read.
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            print(file.read())
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
    except PermissionError:
        print(f"Error: Permission denied for {filename}.")
    except Exception as e:
        print(f"Error: {e}")

def head(filename, lines=10):
    """
    Mimics the Linux 'head' command by displaying the first few lines of a file.
    
    :param filename: Path to the file to read.
    :param lines: Number of lines to display (default is 10).
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            for i, line in enumerate(file):
                if i >= lines:
                    break
                print(line, end="")
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
    except PermissionError:
        print(f"Error: Permission denied for {filename}.")
    except Exception as e:
        print(f"Error: {e}")

def tail(filename, lines=10):
    """
    Mimics the Linux 'tail' command by displaying the last few lines of a file.
    
    :param filename: Path to the file to read.
    :param lines: Number of lines to display (default is 10).
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            content = file.readlines()
            for line in content[-lines:]:
                print(line, end="")
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
    except PermissionError:
        print(f"Error: Permission denied for {filename}.")
    except Exception as e:
        print(f"Error: {e}")

def df():
    """
    Mimics the Linux 'df' command by displaying disk usage statistics in Windows.
    """
    print(f"{'Filesystem':<20}{'Size':<10}{'Used':<10}{'Avail':<10}{'Use%':<10}{'Mounted on'}")
    
    for partition in psutil.disk_partitions(all=True):
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            total = usage.total // (1024 ** 3)  # Convert to GB
            used = usage.used // (1024 ** 3)
            free = usage.free // (1024 ** 3)
            percent = usage.percent
            print(f"{partition.device:<20}{total}G\t{used}G\t{free}G\t{percent}%\t{partition.mountpoint}")
        except PermissionError:
            continue  # Skip drives that can't be accessed

def du(path="."):
    """
    Mimics the Linux 'du' command by calculating the size of a directory and its contents.

    :param path: The directory path to analyze (default is current directory).
    """
    total_size = 0

    for dirpath, dirnames, filenames in os.walk(path):
        for file in filenames:
            file_path = os.path.join(dirpath, file)
            try:
                total_size += os.path.getsize(file_path)
            except FileNotFoundError:
                continue  # Skip if the file was removed during execution

    # Convert size to human-readable format
    size_gb = total_size / (1024 ** 3)
    size_mb = total_size / (1024 ** 2)
    size_kb = total_size / 1024

    print(f"Total size of '{path}':")
    print(f"{size_gb:.2f} GB ({size_mb:.2f} MB / {size_kb:.2f} KB / {total_size} bytes)")

def ps():
    """
    Lists running processes with their Process ID (PID), Name, and Status.

    - `ps` → Displays the list of running processes.
    """
    print(f"{'PID':<10}{'Name':<30}{'Status':<15}")
    print("=" * 55)
    
    for proc in psutil.process_iter(attrs=['pid', 'name', 'status']):
        try:
            print(f"{proc.info['pid']:<10}{proc.info['name']:<30}{proc.info['status']:<15}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

def kill(pid, force=False):
    """
    Kills a process by its PID.

    - `kill <PID>` → Sends a termination signal (SIGTERM).
    - `kill <PID> -f` → Forces termination (SIGKILL).

    If the PID does not exist, an error is displayed.
    """
    try:
        if not psutil.pid_exists(pid):
            print(f"Error: No such process with PID {pid}")
            return

        if force:
            os.kill(pid, signal.SIGKILL)  # Force kill (Linux/Unix)
            print(f"Process {pid} forcefully terminated.")
        else:
            os.kill(pid, signal.SIGTERM)  # Graceful termination
            print(f"Process {pid} terminated.")

    except PermissionError:
        print(f"Error: Permission denied to kill PID {pid}")
    except ProcessLookupError:
        print(f"Error: No such process with PID {pid}")
    except Exception as e:
        print(f"Error: {e}")

def ping(host, count=4):
    """
    Sends ICMP echo requests to a host.

    - `ping <host>` → Pings the host 4 times (default).
    - `ping <host> -c <count>` → Pings the host <count> times.

    Works on both Windows and Linux.
    """
    param = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        result = subprocess.run(
            ["ping", param, str(count), host],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError:
        print(f"Error: Unable to reach {host}")
    except Exception as e:
        print(f"Error: {e}")

def clear():
    os.system("cls")

def shutdown(timer=0):
    """
    Shuts down the system.

    - `shutdown` → Shuts down the system immediately.
    - `shutdown -t <seconds>` → Delays shutdown by <seconds>.

    Works on Windows and Linux/macOS.
    """
    system = platform.system().lower()
    
    if system == "windows":
        cmd = f"shutdown /s /t {timer}"
    else:
        cmd = f"shutdown -h {timer}"

    os.system(cmd)
    print(f"Shutdown command executed. Timer: {timer}s")

def restart(timer=0):
    """
    Restarts the system.

    - `restart` → Restarts the system immediately.
    - `restart -t <seconds>` → Delays restart by <seconds>.

    Works on Windows and Linux/macOS.
    """
    system = platform.system().lower()
    
    if system == "windows":
        cmd = f"shutdown /r /t {timer}"
    else:
        cmd = f"shutdown -r {timer}"

    os.system(cmd)
    print(f"Restart command executed. Timer: {timer}s")

def run_git_command(command_string):
    try:
        os.system(f"git {command_string}")
    except:
        print("git -wrong command!")

def python(command):
    try:
        os.system(f"python {command}")
    except:
        print("Python Command Not Found!")

def pip(command):
    try:
        os.system(f"pip {command}")
    except:
        print("pip wrong command!")