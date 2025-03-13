import subprocess
import time
import os
from termcolor import colored

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
    """Run Sherlock and delete the generated text file after execution."""
    print(f"🔍 Searching for username: {username}")

    # ✅ Corrected path to Sherlock inside 'custom/sherlock/'
    sherlock_path = os.path.join(os.path.dirname(__file__), "sherlock", "sherlock.py")

    # Ensure the file exists before running
    if not os.path.exists(sherlock_path):
        print(f"❌ Sherlock script not found at {sherlock_path}")
        return

    # Run Sherlock script
    subprocess.run(["python", sherlock_path, username], cwd=os.path.dirname(sherlock_path))

    # File created by Sherlock
    result_file = f"{username}.txt"

    # Wait to ensure the file is written
    time.sleep(2)

    # Check if the file exists
    if os.path.exists(result_file):
        try:
            with open(result_file, "r", encoding="utf-8") as file:
                results = file.read().strip()  # Read and remove extra spaces/new lines

            if results:  # ✅ Only print if results exist
                print("\n" + "=" * 50)
                print(f"🔍 Search Results for {username}:")
                print(results)
                print("=" * 50 + "\n")

            os.remove(result_file)  # ✅ Delete file without printing "Deleted temporary file"

        except Exception as e:
            print(f"⚠️ Error deleting file {result_file}: {e}")

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

