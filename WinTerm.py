from time import sleep
from CLI.CLS import home_path
from CLI import CLS_check

def main():
    home_path()
    CLS_check.check_command("clear")

    while True:
        try:
            user_input = input(CLS_check.colorize("WinTerm", "red", None, "bold") + "> ").strip()

            if not user_input:
                continue

            elif user_input == "exit":
                break

            else:
                CLS_check.check_command(user_input)

        except KeyboardInterrupt:
            print(f"\n{CLS_check.colorize("-----Exiting WinTerm-----", "red", None, "bold")} \n")
            sleep(1)
            break

if __name__ == "__main__":
    main()
