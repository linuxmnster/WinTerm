from CLI import CLS

def check_command(raw_input: str):
    command = raw_input.strip().lower()

    if not command:
        return True

    if command in ["cls", "clear"]:
        CLS.clear_screen()

    elif command in ["pwd"]:
        CLS.pwd()

    else:
        print(f"⚠️  Unknown command : {raw_input}")
        