import requests
import os
import sys
import time
import subprocess

setups = os.path.join(os.path.dirname(__file__), "setups")
os.makedirs(setups, exist_ok=True)  # Ensure the folder exists

def download_and_install(url, filename):
    destination_path = os.path.join(setups, filename)
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Check for errors
        
        total_size = int(response.headers.get("content-length", 0))
        downloaded_size = 0
        start_time = time.time()

        with open(destination_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    downloaded_size += len(chunk)
                    elapsed_time = time.time() - start_time
                    speed = downloaded_size / (elapsed_time + 1e-6) / 1024  # KB/s
                    percentage = (downloaded_size / total_size) * 100 if total_size else 0
                    sys.stdout.write(f"\rDownloading: {percentage:.2f}% ({downloaded_size / 1024 / 1024:.2f} MB/{total_size / 1024 / 1024:.2f} MB) @ {speed:.2f} KB/s")
                    sys.stdout.flush()

        print("\nDownload completed:", destination_path)

        # **Automatically run the installer**
        subprocess.run([destination_path], check=True)
        print(f"{filename} installation started...")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
    except subprocess.SubprocessError as e:
        print(f"Error running installer: {e}")

# **Define tools and their URLs**
tools = {
    "wireshark": lambda: download_and_install("https://2.na.dl.wireshark.org/win64/Wireshark-4.4.5-x64.exe", "Wireshark-4.4.5-x64.exe"),
    "nmap": lambda: download_and_install("https://nmap.org/dist/nmap-7.95-setup.exe", "nmap-7.95-setup.exe"),
    "metasploit": lambda: download_and_install("https://windows.metasploit.com/metasploitframework-latest.msi", "metasploitframework-latest.msi"),
    "burpsuite": lambda: download_and_install("https://portswigger.net/burp/releases/startdownload?product=pro&version=2025.1.4&type=WindowsX64", "burpsuite-pro-2025.1.4.exe"),
    "git": lambda: download_and_install("https://github.com/git-for-windows/git/releases/download/v2.44.0.windows.1/Git-2.44.0-64-bit.exe", "Git-2.44.0-64-bit.exe")
}

# **Function to install tools**
def service(options):
    if options.startswith("install "):
        tool_name = options.replace("install ", "").strip()
        if tool_name in tools:
            tools[tool_name]()  # Download and install
        else:
            print("Tool not found. Available tools:", ", ".join(tools.keys()))
    elif options == "list":
        for num, tool in enumerate(tools, start=1):
            print(f"{num}. {tool}")
