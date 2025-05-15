from CLI import CLS_check
from CLI.CLS import home_path

def color(text, code):
    return f"\033[{code}m{text}\033[0m"

def main():
    home_path()

    while True:
        try:
            user_input = input(color("WinTerm", "32")+color("> ", "31")).strip()

            if not user_input:
                continue

            elif user_input == "exit":
                break

            else:
                CLS_check.check_command(user_input)

        except KeyboardInterrupt:
            print("\nExiting WinTerm.")
            break

if __name__ == "__main__":
    main()
