import subprocess
import time
import os
from termcolor import colored
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))

def open_with_nano(file_path):
    """Opens a file in GNU Nano on Windows, assuming nano.exe is inside the 'nano' folder."""
    nano_path = os.path.join(script_dir, "nano", "nano.exe")  # Locate nano.exe

    if not os.path.exists(nano_path):
        print("Error: 'nano.exe' not found in the 'nano' folder.")
        return

    try:
        subprocess.run([nano_path, file_path], check=True)
    except Exception as e:
        print(f"Error: {e}")

def extract_metadata(file_path):
    """Extract metadata using ExifTool on Windows, assuming exiftool.exe is inside the 'exiftool' folder."""
    exiftool_path = os.path.join(script_dir, "exiftool", "exiftool.exe")

    if not os.path.exists(exiftool_path):
        print("Error: 'exiftool.exe' not found in the 'exiftool' folder.")
        return

    try:
        result = subprocess.run([exiftool_path, file_path], capture_output=True, text=True, check=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"ExifTool Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")

def extract_strings(file_path):
    # Path to strings.exe inside the 'strings' folder
    strings_exe = os.path.join(script_dir, "strings", "strings64.exe")

    # Check if strings.exe exists
    if not os.path.exists(strings_exe):
        print("Error: 'strings.exe' not found in the 'strings' folder.")
        return

    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return

    try:
        result = subprocess.run([strings_exe, "-accepteula", file_path], capture_output=True, text=True)

        if result.stdout:
            print(result.stdout)
        else:
            print("No readable strings found.")

    except subprocess.CalledProcessError as e:
        print(f"Strings Extraction Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")

def find_social_accounts(username):
    output_file = "output.txt"
    try:
        print(colored(f"\n🔍 Searching for username: {username}\n", "cyan"))
        with open(output_file, "w") as f:
            subprocess.run(["sherlock", username], stdout=f, stderr=subprocess.DEVNULL, text=True)
        with open(output_file, "r") as f:
            results = f.readlines()
        for line in results:
            if "[+]" in line:
                print(colored(line.strip(), "green"))  
            elif "INFO" in line:
                print(colored(line.strip(), "blue")) 
            elif "ERROR" in line:
                print(colored(line.strip(), "red"))  
            else:
                print(colored(line.strip(), "white"))  
    except Exception as e:
        print(colored(f"❌ Error: {e}", "red"))
    finally:
        time.sleep(1)
        if os.path.exists(output_file):
            os.remove(output_file)

def run_tgpt(command):
    """Runs tgpt.exe with a given string command."""
    tgpt_path = os.path.join(script_dir, "tgpt", "tgpt.exe")  # Locate tgpt.exe

    if not os.path.exists(tgpt_path):
        print("Error: 'tgpt.exe' not found in the 'tgpt' folder.")
        return

    try:
        subprocess.run([tgpt_path, command], check=True)
    except Exception as e:
        print(f"Error: {e}")