import os
import subprocess

# Mapping Linux commands to Windows equivalents
command_map = {
    "ls": "dir",
    "clear": "cls",
    "pwd": "cd",
    "cp": "copy",
    "mv": "move",
    "rm": "del",
    "rmdir": "rd /s /q",
    "cat": "type",
    "touch": "echo. >",
    "echo": "echo",
    "grep": "findstr",
    "whoami": "whoami",
    "uname": "ver",
    "df": "wmic logicaldisk get size,freespace,caption",
    "du": "dir /s",
    "ps": "tasklist",
    "kill": "taskkill /IM",
    "top": "tasklist /v",
    "man": "help",
    "mkdir": "mkdir",
    "rmdir": "rmdir",
    "cd": "cd",
    "exit": "exit",
    "find": "dir /s /b | findstr",
    "locate": "dir /s /b",
    "chmod": "icacls",
    "chown": "takeown",
    "which": "where",
    "curl": "curl",
    "wget": "curl -O",
    "head": "powershell -Command \"Get-Content -Path",
    "tail": "powershell -Command \"Get-Content -Path",
    "ping": "ping",
    "traceroute": "tracert",
    "netstat": "netstat",
    "ifconfig": "ipconfig /all",
    "ip": "ipconfig",
    "hostname": "hostname",
    "uptime": "net stats srv",
    "history": "doskey /history",
    "basename": "for %A in",
    "dirname": "for %A in",
}

# Help documentation for 'man' command
man_pages = {
    "ls": "Lists files in a directory. Equivalent to 'dir' in Windows.",
    "pwd": "Prints the current working directory.",
    "cd": "Changes the current directory.",
    "cp": "Copies files from one location to another.",
    "mv": "Moves or renames files.",
    "rm": "Deletes files. Use 'rmdir' for directories.",
    "mkdir": "Creates a new directory.",
    "rmdir": "Removes an empty directory.",
    "cat": "Displays file contents.",
    "touch": "Creates an empty file.",
    "grep": "Searches for a string in a file. Equivalent to 'findstr'.",
    "whoami": "Displays the current logged-in user.",
    "uname": "Displays system information.",
    "ps": "Shows running processes.",
    "kill": "Terminates a process by name.",
    "top": "Displays running processes with details.",
    "man": "Displays help for commands.",
    "find": "Searches for files with a specific name.",
    "chmod": "Changes file permissions.",
    "chown": "Changes file ownership.",
    "which": "Finds the location of an executable.",
    "ping": "Tests network connectivity to a host.",
    "netstat": "Displays network statistics.",
    "ifconfig": "Shows network configuration. Equivalent to 'ipconfig /all'.",
    "ip": "Displays network configuration details.",
    "uptime": "Shows system uptime.",
    "history": "Displays command history.",
}

def execute_command(user_input):
    parts = user_input.split()
    if not parts:
        return

    command = parts[0]
    args = parts[1:]

    # Handle 'man' command
    if command == "man":
        if args and args[0] in man_pages:
            print(f"{args[0]}: {man_pages[args[0]]}")
        else:
            print("Usage: man <command>\nExample: man ls")
        return

    # Handle 'cd' separately
    if command == "cd":
        try:
            os.chdir(args[0])
        except IndexError:
            print("Usage: cd <directory>")
        except FileNotFoundError:
            print("Directory not found.")
        return

    # Handle mapped commands
    if command in command_map:
        mapped_command = command_map[command]
        full_command = f"{mapped_command} {' '.join(args)}"
    else:
        full_command = user_input  # Assume it's a native Windows command

    # Execute command
    try:
        subprocess.run(full_command, shell=True, check=True)
    except subprocess.CalledProcessError:
        print(f"Error executing: {user_input}")

def main():
    while True:
        try:
            user_input = input("WinTerm$ ").strip()
            if user_input.lower() in ["exit", "quit"]:
                break
            execute_command(user_input)
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
