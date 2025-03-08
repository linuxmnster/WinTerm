import webbrowser
from googlesearch import search
import pyfiglet
from os import system

def google_search(query, num_results=5):
    print("\n🔍 Searching Google for:", query)
    results = list(search(query, num_results=num_results))
    
    for idx, url in enumerate(results, start=1):
        print(f"[{idx}] {url}")
    
    return results

def open_url(selection, results):
    try:
        if selection.isdigit():
            index = int(selection) - 1
            if 0 <= index < len(results):
                print(f"🌍 Opening: {results[index]}")
                webbrowser.open(results[index])
            else:
                print("❌ Invalid selection number.")
        else:
            print(f"🌍 Opening: {selection}")
            webbrowser.open(selection)
    except Exception as e:
        print("❌ Error opening URL:", e)

def show_help():
    print("\nAvailable Commands:")
    print(" google \"query\" -number  → Search Google and list results.")
    print(" use <url/number>  → Open a search result in a web browser.")
    print(" help  → Show this help menu.")
    print(" exit  → Exit the program.")

def main():
    system("cls")
    print(pyfiglet.figlet_format("Google"))
    results = []
    while True:
        command = input("\nGoogleSearch> ").strip()
        
        if command.startswith("google "):
            parts = command.split(" -")
            query = parts[0][7:].strip("\"")
            num_results = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 5
            results = google_search(query, num_results)
        
        elif command.startswith("use "):
            if not results:
                print("❌ No recent search results. Use 'google \"query\" -number' first.")
            else:
                open_url(command[4:], results)
        
        elif command == "help":
            show_help()
        
        elif command == "exit":
            break
        else:
            print("❌ Unknown command. Use 'google \"query\" -number', 'use <url/number>', or 'help'.")

if __name__ == "__main__":
    main()
