import requests
import pyfiglet

def check_username(username):
    platforms = {
        "GitHub": f"https://github.com/{username}",
        "Twitter": f"https://twitter.com/{username}",
        "Instagram": f"https://www.instagram.com/{username}/",
        "Facebook": f"https://www.facebook.com/{username}",
        "TikTok": f"https://www.tiktok.com/@{username}",
        "Reddit": f"https://www.reddit.com/user/{username}",
        "LinkedIn": f"https://www.linkedin.com/in/{username}",
        "Pinterest": f"https://www.pinterest.com/{username}/"
    }
    
    print(f"\n🔍 Searching for username: {username}\n")
    
    for platform, url in platforms.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {platform}: {url}")
            else:
                print(f"❌ {platform}: Not Found")
        except requests.exceptions.RequestException:
            print(f"⚠️ {platform}: Request Failed")

def show_help():
    print("\nAvailable Commands:")
    print(" sherlock <username> → Find username across social media.")
    print(" help → Show this help menu.")
    print(" exit → Exit the program.")

def main():
    print(pyfiglet.figlet_format("Sherlock"))
    while True:
        command = input("\nSherlock> ").strip().split()
        if not command:
            continue
        
        if command[0] == "sherlock" and len(command) == 2:
            check_username(command[1])
        
        elif command[0] == "help":
            show_help()
        
        elif command[0] == "exit":
            break
        else:
            print("❌ Unknown command. Use 'help' to see available commands.")

if __name__ == "__main__":
    main()
