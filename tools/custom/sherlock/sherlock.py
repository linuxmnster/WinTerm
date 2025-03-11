import requests
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
    """Find social media accounts for the given username."""
    
    def check_username(platform, url):
        """Check if the username exists on a given platform."""
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(colored(f"[✔] {platform}: {url}", "green"))
            else:
                print(colored(f"[✘] {platform}", "red"))
        except requests.exceptions.RequestException:
            print(colored(f"[✘] Error checking {platform}", "red"))

    print(colored(f"\n🔍 Searching for username: {username}\n", "cyan"))

    with ThreadPoolExecutor(max_workers=10) as executor:
        for platform, url_template in SOCIAL_MEDIA_PLATFORMS.items():
            url = url_template.format(username)
            executor.submit(check_username, platform, url)

    print(colored("\n✅ Search completed!\n", "yellow"))
