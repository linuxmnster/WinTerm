import requests
import os
from termcolor import colored
from concurrent.futures import ThreadPoolExecutor

# Social media platforms and profile URL formats
SOCIAL_MEDIA_PLATFORMS = {
    "Facebook": "https://www.facebook.com/{}",
    "Instagram": "https://www.instagram.com/{}",
    "Twitter (X)": "https://twitter.com/{}",
    "TikTok": "https://www.tiktok.com/@{}",
    "YouTube": "https://www.youtube.com/{}",
    "Reddit": "https://www.reddit.com/user/{}",
    "GitHub": "https://github.com/{}",
    "Pinterest": "https://www.pinterest.com/{}",
    "Snapchat": "https://www.snapchat.com/add/{}",
    "LinkedIn": "https://www.linkedin.com/in/{}",
    "Discord": "https://discord.com/users/{}",
    "Medium": "https://medium.com/@{}",
    "Twitch": "https://www.twitch.tv/{}",
    "Flickr": "https://www.flickr.com/people/{}",
    "Steam": "https://steamcommunity.com/id/{}",
    "Vimeo": "https://vimeo.com/{}",
}

def find_social_accounts(username):
    """Find social media accounts for the given username and store results in a temporary file."""
    
    temp_file = "results.txt"

    def check_username(platform, url):
        """Check if the username exists on a given platform."""
        try:
            response = requests.get(url, timeout=5)
            with open(temp_file, "a") as file:
                if response.status_code == 200:
                    file.write(f"[✔] {platform}: {url}\n")
                else:
                    file.write(f"[✘] {platform}\n")
        except requests.exceptions.RequestException:
            with open(temp_file, "a") as file:
                file.write(f"[✘] Error checking {platform}\n")

    print(colored(f"\n🔍 Searching for username: {username}\n", "cyan"))

    with ThreadPoolExecutor(max_workers=10) as executor:
        for platform, url_template in SOCIAL_MEDIA_PLATFORMS.items():
            url = url_template.format(username)
            executor.submit(check_username, platform, url)

    # Print results and delete file
    print(colored("\n🔹 Results:\n", "yellow"))
    with open(temp_file, "r") as file:
        for line in file:
            print(colored(line.strip(), "green" if "[✔]" in line else "red"))

    os.remove(temp_file)  # Remove the file after displaying results
    print(colored("\n✅ Search completed!\n", "yellow"))
