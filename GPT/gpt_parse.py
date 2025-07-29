import subprocess
import os

def tgpt_command(raw_input: str):
    query = raw_input.strip()[4:].strip()

    if not query:
        print("Usage: tgpt \"your query\"")
        return

    # Full path to tgpt.exe (always in GPT folder)
    tgpt_path = os.path.join(os.path.dirname(__file__), "tgpt.exe")

    if not os.path.exists(tgpt_path):
        print("❌ tgpt.exe not found in GPT folder.")
        return

    try:
        # Run tgpt.exe with the query
        subprocess.run(f'"{tgpt_path}" "{query}"', shell=True)
    except Exception as e:
        print(f"❌ Failed to run tgpt.exe: {e}")

import subprocess
import webbrowser
import shutil
import sys
import os

def is_ollama_installed():
    return shutil.which("ollama") is not None

def install_ollama():
    if sys.platform.startswith("win"):
        print("🔄 Ollama not found. Attempting to download and launch installer...")
        try:
            subprocess.run([
                "powershell", "-Command",
                "Invoke-WebRequest https://ollama.com/download/OllamaSetup.exe -OutFile $env:TEMP\\OllamaSetup.exe; "
                "Start-Process $env:TEMP\\OllamaSetup.exe -Wait"
            ], check=True)
            print("✅ Ollama setup launched. Please complete the installation manually and restart.")
        except subprocess.CalledProcessError:
            print("❌ Failed to download or run the Ollama installer.")
    else:
        print("❌ Ollama auto-install not supported on this OS. Please install it from https://ollama.com/download")

def run_ollama_command(args: list):
    try:
        subprocess.run(["ollama"] + args)
    except Exception as e:
        print(f"❌ Failed to run ollama command: {e}")

def handle_gpt_command(raw_input: str):
    parts = raw_input.strip().split()
    if len(parts) < 2:
        print("Usage:")
        print("  gpt install <model>")
        print("  gpt uninstall <model>")
        print("  gpt run <model>")
        print("  gpt list")
        print("  gpt malist")
        return

    action = parts[1].lower()

    if action == "malist":
        webbrowser.open("https://ollama.com/search")
        return

    if not is_ollama_installed():
        install_ollama()
        return

    if action == "install" and len(parts) >= 3:
        model = parts[2]
        print(f"📥 Installing model: {model}")
        run_ollama_command(["pull", model])

    elif action == "uninstall" and len(parts) >= 3:
        model = parts[2]
        print(f"🗑️ Uninstalling model: {model}")
        run_ollama_command(["rm", model])

    elif action == "run" and len(parts) >= 3:
        model = parts[2]
        print(f"🚀 Running model: {model}")
        run_ollama_command(["run", model])

    elif action == "list":
        print("📦 Installed Models:")
        run_ollama_command(["list"])

    else:
        print("❌ Invalid GPT command or missing argument.")
