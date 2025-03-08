import os
import pyfiglet

def hide_file(cover_file, secret_file, output_file, password):
    command = f"steghide embed -cf {cover_file} -ef {secret_file} -sf {output_file} -p {password}"
    os.system(command)
    print("✅ File hidden successfully!")

def extract_file(stego_file, output_file, password):
    command = f"steghide extract -sf {stego_file} -xf {output_file} -p {password}"
    os.system(command)
    print("✅ File extracted successfully!")

def change_directory(path):
    try:
        os.chdir(path)
        print(f"📁 Changed directory to: {os.getcwd()}")
    except FileNotFoundError:
        print("❌ Directory not found.")
    except PermissionError:
        print("❌ Permission denied.")

def list_directory():
    for item in os.listdir():
        print(item)

def show_current_directory():
    print("📍 Current Directory:", os.getcwd())

def move_file(source, destination):
    try:
        os.rename(source, destination)
        print("✅ File moved successfully!")
    except Exception as e:
        print("❌ Error moving file:", e)

def copy_file(source, destination):
    try:
        os.system(f"cp {source} {destination}")
        print("✅ File copied successfully!")
    except Exception as e:
        print("❌ Error copying file:", e)

def show_help():
    print("\nAvailable Commands:")
    print(" hide <cover_file> <secret_file> <output_file> <password> → Hide a file inside another.")
    print(" extract <stego_file> <output_file> <password> → Extract a hidden file.")
    print(" cd <path> → Change directory.")
    print(" ls → List files in the current directory.")
    print(" pwd → Show current directory.")
    print(" mv <source> <destination> → Move a file.")
    print(" cp <source> <destination> → Copy a file.")
    print(" help  → Show this help menu.")
    print(" exit  → Exit the program.")

def main():
    print(pyfiglet.figlet_format("StegHide Tool"))
    while True:
        command = input("\nStegHide> ").strip().split()
        
        if not command:
            continue
        
        if command[0] == "hide" and len(command) == 5:
            hide_file(command[1], command[2], command[3], command[4])
        
        elif command[0] == "extract" and len(command) == 4:
            extract_file(command[1], command[2], command[3])
        
        elif command[0] == "cd" and len(command) == 2:
            change_directory(command[1])
        
        elif command[0] == "ls":
            list_directory()
        
        elif command[0] == "pwd":
            show_current_directory()
        
        elif command[0] == "mv" and len(command) == 3:
            move_file(command[1], command[2])
        
        elif command[0] == "cp" and len(command) == 3:
            copy_file(command[1], command[2])
        
        elif command[0] == "help":
            show_help()
        
        elif command[0] == "exit":
            break
        else:
            print("❌ Unknown command. Use 'help' to see available commands.")

if __name__ == "__main__":
    main()