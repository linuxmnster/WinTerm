from .custom import gsearch, steghide, phone_osint, sherlock, exiftool, binwalk
def check(tool):
    if tool == "googlesearch":
        gsearch.main()

    elif tool == "steghide":
        steghide.main

    elif tool == "phoneosint":
        phone_osint.main()

    elif tool == "sherlock":
        sherlock.main()
    
    elif tool == "exiftool":
        exiftool.main()

    elif tool == "binwalk":
        binwalk.main()

    else:
        print(f"No Tool Named {tool} Was Found!")
