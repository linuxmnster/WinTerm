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
