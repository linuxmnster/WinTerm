from .custom import finder

def check(rn):
    """Validate and execute commands based on user input."""
    
    # Sherlock: Finds social accounts
    if rn.startswith("sherlock "):
        username = rn[9:].strip()  # Extract the username
        if username:
            finder.find_social_accounts(username)
        else:
            print("❌ Usage: sherlock <username>")

    # Open with Nano
    elif rn.startswith("nano "):
        finder.open_with_nano(rn[5:].strip())

    # Extract metadata using ExifTool
    elif rn.startswith("exiftool "):
        finder.extract_metadata(rn[9:].strip())

    # Extract strings from a file
    elif rn.startswith("strings "):
        finder.extract_strings(rn[8:].strip())

    # Get file details
    elif rn.startswith("file "):
        finder.find_file_details(rn[5:].strip())

    # Run Terminal GPT (tgpt)
    elif rn.startswith("tgpt "):
        finder.run_tgpt(rn[5:].strip())

    # Perform binwalk analysis
    elif rn.startswith("binwalk "):
        finder.binwalk(rn[8:].strip())

    else:
        print("❌ Invalid command. Type 'help' to see available commands.")
