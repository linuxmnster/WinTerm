import os
import pyfiglet
import subprocess

def scan_file(file_path):
    try:
        print(f"\n🔍 Scanning file: {file_path}\n")
        result = subprocess.run(["binwalk", file_path], capture_output=True, text=True)
        print(result.stdout)
    except FileNotFoundError:
        print("❌ Binwalk is not installed. Please install it using 'sudo apt install binwalk' (Linux) or 'brew install binwalk' (MacOS).")
    except Exception as e:
        print("❌ Error scanning file:", e)

def show_help():
    print("\nAvailable Commands:")
    print(" binwalk <file> → Scan file for hidden data.")
    print(" help → Show this help menu.")
    print(" exit → Exit the program.")

def main():
    print(pyfiglet.figlet_format("Binwalk"))
    while True:
        command = input("\nBinwalk> ").strip().split()
        if not command:
            continue
        
        if command[0] == "binwalk" and len(command) == 2:
            file_path = command[1]
            if not os.path.exists(file_path):
                print("❌ File not found.")
            else:
                scan_file(file_path)
        
        elif command[0] == "help":
            show_help()
        
        elif command[0] == "exit":
            break
        else:
            print("❌ Unknown command. Use 'help' to see available commands.")

if __name__ == "__main__":
    main()
