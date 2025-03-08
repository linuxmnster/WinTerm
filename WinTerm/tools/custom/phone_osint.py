import phonenumbers
import webbrowser
import pyfiglet
from phonenumbers import geocoder, carrier, timezone

def validate_number(phone):
    try:
        parsed_number = phonenumbers.parse(phone)
        if not phonenumbers.is_valid_number(parsed_number):
            print("❌ Invalid phone number.")
            return None
        return parsed_number
    except:
        print("❌ Invalid phone number format.")
        return None

def get_phone_info(phone):
    parsed_number = validate_number(phone)
    if parsed_number:
        print("\n📌 Phone Number Information:")
        print(f"📍 Country: {geocoder.description_for_number(parsed_number, 'en')}")
        print(f"📡 Carrier: {carrier.name_for_number(parsed_number, 'en')}")
        print(f"⏳ Time Zone: {timezone.time_zones_for_number(parsed_number)}")

def google_search(phone):
    query = f"{phone} phone number"
    url = f"https://www.google.com/search?q={query}"
    print("🌍 Opening Google search results...")
    webbrowser.open(url)

def show_help():
    print("\nAvailable Commands:")
    print(" lookup <phone_number> → Get country, carrier, and timezone information.")
    print(" google <phone_number> → Search phone number on Google.")
    print(" help → Show this help menu.")
    print(" exit → Exit the program.")

def main():
    print(pyfiglet.figlet_format("Phone OSINT"))
    while True:
        command = input("\nPhoneOSINT> ").strip().split()
        if not command:
            continue
        
        if command[0] == "lookup" and len(command) == 2:
            get_phone_info(command[1])
        
        elif command[0] == "google" and len(command) == 2:
            google_search(command[1])
        
        elif command[0] == "help":
            show_help()
        
        elif command[0] == "exit":
            break
        else:
            print("❌ Unknown command. Use 'help' to see available commands.")

if __name__ == "__main__":
    main()
