# tools/install_tools.py
"""
Auto-bootstrap & installer functions for WinTerm tools.

This file does two things:
  1) Best-effort "ensure" functions that try to install missing package managers/tools:
       - chocolatey (choco)  [requires admin]
       - scoop               [user install, no admin usually]
       - git                 [tries scoop/choco or direct installer]
       - pip                 [ensurepip or get-pip.py]
       - winget              [best-effort; may not be possible on some systems]
  2) Manifest-driven tool installers that use available package managers (winget/choco/scoop/pip/git/download)
     to install target cybersecurity tools.

Notes:
 - Many installs require network access and may require admin privileges (UAC).
 - This script is best-effort; it prints detailed guidance where automatic install is not possible.
"""

import os
import sys
import shutil
import subprocess
import tempfile
import time
from urllib import request

# -----------------------
# Low-level helpers
# -----------------------
def _which(prog: str) -> bool:
    return shutil.which(prog) is not None

def _run(cmd, shell=False, timeout=None):
    try:
        if shell:
            res = subprocess.run(cmd, shell=True, timeout=timeout)
        else:
            # ensure list usage when passing list
            if isinstance(cmd, (list, tuple)):
                res = subprocess.run(cmd, timeout=timeout)
            else:
                res = subprocess.run(cmd, shell=True, timeout=timeout)
        return res.returncode == 0
    except Exception:
        return False

def _run_elevated_windows(command):
    """
    On Windows, use PowerShell Start-Process to prompt for elevation and run the given cmd string.
    Returns True if the Start-Process invocation succeeded (user still may need to accept UAC).
    """
    if not sys.platform.startswith("win"):
        return _run(command, shell=True)
    try:
        ps_cmd = f'Start-Process cmd -ArgumentList "/c {command}" -Verb RunAs'
        return _run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd])
    except Exception:
        return False

def _download_file(url, dest):
    try:
        # Use urlretrieve for simplicity
        request.urlretrieve(url, dest)
        return True
    except Exception:
        return False

def _git_clone(repo_url, dest_dir):
    if not _which("git"):
        return False
    return _run(["git", "clone", "--depth", "1", repo_url, dest_dir])

# -----------------------
# Ensure package managers & basic tools
# -----------------------

def ensure_chocolatey():
    """
    Install Chocolatey if missing. Requires admin (will prompt UAC).
    Returns True if choco is available at the end.
    """
    if _which("choco"):
        print("choco already installed.")
        return True

    print("[ensure] Chocolatey not found. Attempting to install (requires Administrator)...")
    # Official install script (PowerShell)
    ps_cmd = (
        "Set-ExecutionPolicy Bypass -Scope Process -Force; "
        "iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
    )
    # Run elevated so Chocolatey can install to ProgramData
    ok = _run_elevated_windows(f"powershell -NoProfile -ExecutionPolicy Bypass -Command \"{ps_cmd}\"")
    # small wait for path update
    time.sleep(2)
    if ok and _which("choco"):
        print("[ensure] Chocolatey installed.")
        return True

    print("[ensure] Chocolatey installation failed or requires manual steps. Please install Chocolatey manually: https://chocolatey.org/install")
    return False

def ensure_scoop():
    """
    Install Scoop if missing. Scoop installs to user profile and usually does not require admin.
    Returns True if scoop is available.
    """
    if _which("scoop"):
        print("scoop already installed.")
        return True

    print("[ensure] Scoop not found. Attempting user install (no admin) ...")
    # Install using PowerShell (current user)
    ps_cmd = (
        "Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force; "
        "iwr -useb get.scoop.sh | iex"
    )
    ok = _run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd])
    time.sleep(1)
    if ok and _which("scoop"):
        print("[ensure] Scoop installed.")
        return True

    print("[ensure] Scoop install failed. You can install manually: https://scoop.sh/")
    return False

def ensure_git():
    """
    Ensure git is available. Tries the following:
      - If git exists -> ok
      - If scoop available -> scoop install git
      - If choco available -> choco install git -y
      - Fallback: download official installer and run it (elevated)
    """
    if _which("git"):
        print("git already installed.")
        return True

    print("[ensure] git not found. Attempting to install git...")

    # try scoop
    if _which("scoop"):
        print("[ensure] Trying scoop install git ...")
        if _run(["scoop", "install", "git"]):
            return True

    # try choco
    if _which("choco"):
        print("[ensure] Trying choco install git ... (may require admin)")
        if _run(["choco", "install", "-y", "git"]):
            return True

    # Fallback: download official Git for Windows installer and launch elevated
    print("[ensure] Trying to download Git for Windows installer...")
    git_url = "https://github.com/git-for-windows/git/releases/latest/download/Git-2.41.0-64-bit.exe"
    # note: version in URL may change; we attempt latest release path could be used
    dest = os.path.join(tempfile.gettempdir(), "git-installer.exe")
    if _download_file(git_url, dest):
        print("[ensure] Downloaded Git installer. Launching installer (UAC may be required).")
        _run_elevated_windows(f'"{dest}"')
        return _which("git")
    print("[ensure] Failed to auto-install git. Please install git manually: https://git-scm.com/download/win")
    return False

def ensure_pip():
    """
    Ensure pip is available for the running Python interpreter.
    Tries ensurepip, then get-pip.py if needed.
    """
    try:
        import pip  # type: ignore
        print("pip already available.")
        return True
    except Exception:
        pass

    print("[ensure] pip not found. Attempting to bootstrap pip...")

    # Try ensurepip in the current interpreter
    try:
        import ensurepip
        ensurepip.bootstrap(upgrade=True)
        print("[ensure] pip installed via ensurepip.")
        return True
    except Exception:
        pass

    # Fallback: download get-pip.py and run it
    get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
    dest = os.path.join(tempfile.gettempdir(), "get-pip.py")
    if _download_file(get_pip_url, dest):
        if _run([sys.executable, dest]):
            print("[ensure] pip installed via get-pip.py.")
            return True

    print("[ensure] Failed to auto-install pip. Please install pip manually.")
    return False

def ensure_winget():
    """
    Best-effort attempt to get winget. winget (App Installer) is typically provided via Microsoft Store
    and distributed as an MSIX package; programmatic installation is not reliable on all Windows versions.
    This function will attempt to see if App Installer is available; if not, it will try a best-effort route.
    Returns True if winget is available.
    """
    if _which("winget"):
        print("winget already installed.")
        return True

    print("[ensure] winget not found. Attempting best-effort installation...")

    # On many systems, winget is installed as part of App Installer from Microsoft Store.
    # Programmatic silent installation of App Installer via Store is not reliable.
    # We'll attempt to use the Microsoft release of the App Installer MSIX bundle (best-effort).
    # If this fails, inform the user that winget must be installed via Microsoft Store / OS update.

    # Best-effort: try to use winget-cli's msixbundle from GitHub releases (if available)
    # Note: this may fail depending on OS version and Store configuration.
    try:
        # There isn't a stable universal URL to download App Installer for all Windows versions,
        # so we fall back to user guidance instead of risking a broken install attempt.
        print("[ensure] Automatic winget install is not reliably supported across Windows versions.")
        print("[ensure] Please install 'App Installer' from Microsoft Store or update Windows to get winget.")
        return False
    except Exception:
        return False

def ensure_package_managers():
    """
    Ensure commonly used package managers and tools are available (best-effort).
    Returns a dict of results.
    """
    results = {}
    # For reliable automation prefer non-interactive user-space installations first
    results["scoop"] = ensure_scoop()
    # pip is required for some Python installs
    results["pip"] = ensure_pip()
    # Try chocolatey (may require admin)
    results["choco"] = ensure_chocolatey()
    # git
    results["git"] = ensure_git()
    # winget best-effort
    results["winget"] = ensure_winget()
    return results

# -----------------------
# Manifest-driven installation (as before)
# -----------------------
def _install_via_managers(manifest):
    """
    Try to install using available managers in preferred order:
    winget -> choco -> scoop -> pip -> git -> download & run
    """
    # winget
    winget_id = manifest.get("winget_id")
    if winget_id and _which("winget"):
        print(f"Trying winget install: {winget_id}")
        if _run(["winget", "install", "--id", winget_id, "--silent"]):
            return True

    # choco
    choco_id = manifest.get("choco_id")
    if choco_id and _which("choco"):
        print(f"Trying choco install: {choco_id}")
        if _run(["choco", "install", "-y", choco_id]):
            return True

    # scoop
    scoop_id = manifest.get("scoop_id")
    if scoop_id and _which("scoop"):
        print(f"Trying scoop install: {scoop_id}")
        if _run(["scoop", "install", scoop_id]):
            return True

    # pip
    pip_pkg = manifest.get("pip_pkg")
    if pip_pkg and ensure_pip():
        print(f"Trying pip install: {pip_pkg}")
        if _run([sys.executable, "-m", "pip", "install", "--user", pip_pkg]):
            return True

    # git clone
    git_repo = manifest.get("git_repo")
    if git_repo and _which("git"):
        print(f"Trying git clone: {git_repo}")
        td = tempfile.mkdtemp(prefix="winterm_")
        if _git_clone(git_repo, td):
            # try pip install -e or setup.py
            if os.path.exists(os.path.join(td, "setup.py")):
                if _run([sys.executable, os.path.join(td, "setup.py"), "install", "--user"]):
                    return True
            if _run([sys.executable, "-m", "pip", "install", "--user", "-e", td]):
                return True
            print(f"Cloned to {td}. Manual build may still be required.")
            return True

    # download_url
    download_url = manifest.get("download_url")
    if download_url:
        fname = os.path.basename(download_url.split("?")[0]) or "installer.bin"
        dest = os.path.join(tempfile.gettempdir(), fname)
        print(f"Attempting to download installer: {download_url}")
        if _download_file(download_url, dest):
            print(f"Downloaded to {dest}. Attempting to run installer (elevation may be required).")
            if sys.platform.startswith("win"):
                _run_elevated_windows(f'"{dest}"')
                return True
            else:
                if _run(f"chmod +x '{dest}' && '{dest}'", shell=True):
                    return True
        else:
            print("Download failed.")

    return False

# Basic manifests for top tools
_MANIFESTS = {
    "nmap": {
        "winget_id": "Nmap.Nmap",
        "choco_id": "nmap",
        "scoop_id": "nmap",
        "download_url": "https://nmap.org/dist/nmap-7.93-setup.exe",
    },
    "wireshark": {
        "winget_id": "WiresharkFoundation.Wireshark",
        "choco_id": "wireshark",
        "download_url": "https://www.wireshark.org/download/win64/Wireshark-win64.exe",
    },
    "metasploit": {
        "winget_id": "Rapid7.Metasploit",
        "choco_id": "metasploit",
        # best-effort download; may change
        "download_url": "https://downloads.metasploit.com/data/releases/metasploit-latest-windows-x64-installer.exe",
    },
    "burpsuite": {
        "winget_id": "PortSwigger.BurpSuite",
        "download_url": "https://portswigger.net/burp/releases/download?product=community&version=latest",
    },
    "john": {
        "git_repo": "https://github.com/openwall/john",
    },
    "hydra": {
        "git_repo": "https://github.com/vanhauser-thc/thc-hydra",
    },
    "aircrack": {
        "git_repo": "https://github.com/aircrack-ng/aircrack-ng",
    },
    "nikto": {
        "git_repo": "https://github.com/sullo/nikto",
    },
    "sqlmap": {
        "git_repo": "https://github.com/sqlmapproject/sqlmap",
        "download_url": "https://github.com/sqlmapproject/sqlmap/releases/latest/download/sqlmap.zip",
    },
    "hashcat": {
        "winget_id": "hashcat.hashcat",
        "download_url": "https://hashcat.net/files/hashcat-6.2.6.7z",
    },
    "openvas": {
        "git_repo": "https://github.com/greenbone/gsa",
    },
    "ncat": {
        "alias_of": "nmap",
    },
    "theharvester": {
        "pip_pkg": "theHarvester",
        "git_repo": "https://github.com/laramies/theHarvester",
    },
    "autopsy": {
        "download_url": "https://github.com/sleuthkit/autopsy/releases/latest/download/autopsy_windows.zip",
    },
    "owasp-zap": {
        "winget_id": "OWASP.ZAP",
        "download_url": "https://github.com/zaproxy/zaproxy/releases/latest/download/ZAP_2_latest_Windows.exe",
    },
}

# -----------------------
# Public installer functions
# -----------------------
def _install_from_manifest(key: str) -> bool:
    manifest = _MANIFESTS.get(key)
    if not manifest:
        print(f"No manifest for {key}")
        return False

    if "alias_of" in manifest:
        return _install_from_manifest(manifest["alias_of"])

    # Ensure some managers available (best-effort)
    ensure_package_managers()

    success = _install_via_managers(manifest)
    if success:
        print(f"[{key}] Installation attempt finished (either installed or installer launched).")
        return True

    print(f"[{key}] Automated installation failed or was not possible.")
    return False

# Thin wrappers
def install_nmap(): return _install_from_manifest("nmap")
def install_wireshark(): return _install_from_manifest("wireshark")
def install_metasploit(): return _install_from_manifest("metasploit")
def install_burpsuite(): return _install_from_manifest("burpsuite")
def install_john(): return _install_from_manifest("john")
def install_hydra(): return _install_from_manifest("hydra")
def install_aircrack(): return _install_from_manifest("aircrack")
def install_nikto(): return _install_from_manifest("nikto")
def install_sqlmap(): return _install_from_manifest("sqlmap")
def install_hashcat(): return _install_from_manifest("hashcat")
def install_openvas(): return _install_from_manifest("openvas")
def install_ncat(): return _install_from_manifest("ncat")
def install_theharvester(): return _install_from_manifest("theharvester")
def install_autopsy(): return _install_from_manifest("autopsy")
def install_owasp_zap(): return _install_from_manifest("owasp-zap")

def available_installers():
    return {
        "nmap": install_nmap,
        "wireshark": install_wireshark,
        "metasploit": install_metasploit,
        "burpsuite": install_burpsuite,
        "john": install_john,
        "hydra": install_hydra,
        "aircrack": install_aircrack,
        "nikto": install_nikto,
        "sqlmap": install_sqlmap,
        "hashcat": install_hashcat,
        "openvas": install_openvas,
        "ncat": install_ncat,
        "theharvester": install_theharvester,
        "autopsy": install_autopsy,
        "owasp-zap": install_owasp_zap,
    }
