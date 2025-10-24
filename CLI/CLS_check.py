from . import CLS
import os

#color function
def colorize(text, text_color=None, bg_color=None, style=None):
    codes = []

    # Text styles
    styles = {
        "reset": 0,
        "bold": 1,
        "dim": 2,
        "italic": 3,
        "underline": 4,
        "blink": 5,
        "reverse": 7,
        "hidden": 8,
        "strikethrough": 9
    }

    # Text colors
    text_colors = {
        "black": 30, "red": 31, "green": 32, "yellow": 33,
        "blue": 34, "magenta": 35, "cyan": 36, "white": 37,
        "bright_black": 90, "bright_red": 91, "bright_green": 92,
        "bright_yellow": 93, "bright_blue": 94, "bright_magenta": 95,
        "bright_cyan": 96, "bright_white": 97
    }

    # Background colors
    bg_colors = {
        "black": 40, "red": 41, "green": 42, "yellow": 43,
        "blue": 44, "magenta": 45, "cyan": 46, "white": 47,
        "bright_black": 100, "bright_red": 101, "bright_green": 102,
        "bright_yellow": 103, "bright_blue": 104, "bright_magenta": 105,
        "bright_cyan": 106, "bright_white": 107
    }

    # Apply style if valid
    if style in styles:
        codes.append(str(styles[style]))

    # Apply text color if valid
    if text_color in text_colors:
        codes.append(str(text_colors[text_color]))

    # Apply background color if valid
    if bg_color in bg_colors:
        codes.append(str(bg_colors[bg_color]))

    if not codes:
        return text  # No color/style applied

    return f"\033[{';'.join(codes)}m{text}\033[0m"

#packages installer
def update():
    pass

#commands
def check_command(raw_input: str):
    command = raw_input.strip()

    if not command:
        return True

    base = command.split()[0].lower()

    if base in ["cls", "clear"]:
        CLS.clear_screen()

    elif base == "pwd":
        CLS.pwd()

    elif base == "sudo":
        CLS.sudo_command()

    elif base == "ls":
        CLS.ls_command(command)
        print()

    elif base.startswith("cd"):
        CLS.cd_command(raw_input)

    elif base.startswith("mkdir"):
        CLS.mkdir_command(raw_input)

    elif base.startswith("rmdir"):
        CLS.rmdir_command(raw_input)

    elif base.startswith("touch"):
        CLS.touch_command(raw_input)

    elif base.startswith("cat"):
        CLS.cat_command(raw_input)
    
    elif base.startswith("rm"):
        CLS.rm_command(raw_input)

    elif base.startswith("cp"):
        CLS.cd_command(raw_input)

    elif base.startswith("mv"):
        CLS.mv_command(raw_input)
    
    elif base.startswith("head"):
        CLS.head_command(raw_input)

    elif base.startswith("tail"):
        CLS.tail_command(raw_input)

    elif base.startswith("tree"):
        CLS.tree_command(raw_input)

    elif base.startswith("find"):
        CLS.find_command(raw_input)

    elif base.startswith("df"):
        CLS.df_command(raw_input)

    elif base.startswith("du"):
        CLS.du_command(raw_input)

    elif base.startswith("ps"):
        CLS.ps_command(raw_input)

    elif base.startswith("top"):
        CLS.top_command(raw_input)
    
    elif base.startswith("kill"):
        CLS.kill_command(raw_input)

    elif base.startswith("uname"):
        CLS.uname_command(raw_input)

    elif base.startswith("shutdown"):
        CLS.shutdown_command(raw_input)

    elif base.startswith("reboot"):
        CLS.reboot_command(raw_input)

    elif base.startswith("grep"):
        CLS.grep_command(raw_input)

    elif base.startswith("diff"):
        CLS.diff_command(raw_input)
    
    elif base == "nano":
        nano_path = os.path.join(os.path.dirname(__file__), "nano.exe")
        
        if not os.path.exists(nano_path):
            print("❌ nano.exe not found in CLI folder.")
        else:
            args = command[len(base):].strip()
            if not args:
                print("Usage: nano <filename>")
            else:
                import subprocess
                try:
                    subprocess.run([nano_path] + args.split())
                except Exception as e:
                    print(f"❌ Failed to run nano: {e}")

    else:
        # Fallback for unknown commands
        def execute_unknown_command(raw_input, base):
            interactive_cmds = ['python', 'node', 'powershell', 'cmd']

            cmd_name = base.lower().split()[0]

            if cmd_name in interactive_cmds:
                try:
                    subprocess.call(raw_input, shell=True)
                except Exception:
                    print(f"{base}: command failed")
            else:
                try:
                    result = subprocess.run(
                        raw_input, shell=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                    )

                    # Suppress CMD's error and show only your own
                    if result.returncode != 0 and (
                        "not recognized as an internal or external command" in result.stderr
                        or "cannot find the path specified" in result.stderr
                        or "is not recognized" in result.stdout
                    ):
                        print(f"{base}: command not found")
                    else:
                        if result.stdout.strip():
                            print(result.stdout, end="")
                        if result.stderr.strip():
                            print(result.stderr, end="")

                except Exception:
                    print(f"{base}: command not found")

        execute_unknown_command(raw_input, base)

