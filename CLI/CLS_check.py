from . import CLS

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

    else:
        print(f"⚠️  Unknown command: {command}")
