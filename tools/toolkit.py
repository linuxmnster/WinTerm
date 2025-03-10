from .custom import finder
import os

def check(rn):
    if rn == "nano " + rn[5:]:
        finder.open_with_nano(rn[5:])
    
    elif rn == "sherlock " + rn[9:]:
        finder.find_social_accounts(rn[9:])
    
    elif rn == "exiftool " + rn[9:]:
        finder.extract_metadata(rn[9:])

    elif rn == "strings " + rn[8:]:
        finder.extract_strings(rn[8:])