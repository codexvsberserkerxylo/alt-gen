# made by nick (.weound)
# made at 3:30 pm 5/16/2026 probably
# if u use this for actual alt generating then atleast credit me :pleading-face:

# 67 mango gen

# imports
import time
import random
import string
import threading
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from colorama import Fore, Style, init

# init colors (why am i making this comment)
init(autoreset=True)

# config
headless = True # if headless = true then u dont see the browser i would use false tho
threads = 3 # how many browsers
attempts = 50 # how many attempts / how many accounts, at around 20 there will be captchas if u dont use a proxy wtv
output = "accounts.txt" # output file obvs
webhook = "webhook_here" # webhook if u have one

file_lock = threading.Lock()

def send_webhook(username, success, time_taken, error_msg="None"): # func to send webhook
    if not webhook or "your_discord" in webhook: return
    color = 0x00ff00 if success else 0xff0000
    payload = {
        "embeds": [{
            "title": "67 mango gen report", # title of webhook
            "color": color,
            "fields": [ # aaaaaaaaa
                {"name": "status", "value": "success" if success else "failed", "inline": True},
                {"name": "user", "value": f"`{username}`", "inline": True},
                {"name": "time", "value": f"{time_taken:.2f}s", "inline": True},
                {"name": "detail", "value": error_msg, "inline": False}
            ],
            "footer": {"text": "67 mango gen"}
        }]
    }
    try: requests.post(webhook, json=payload)
    except: pass

# func to gen pass and name
def gen_creds():
    suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    user = f"lunar_{suffix}" # makes account like "lunar_x9sXjs9" or wtv, makes u look like a bot, if u want add a table with starting names like "XxMonkey" and then the chars
    cchars = string.ascii_letters + string.digits + "()!§$%&=?*#+/"
    cpass = "lunarx" + ''.join(random.choices(cchars, k=16)) # complex pass (lunar x branded obvs)
    return user, cpass

def create_account(): # creates account (if u can read its obvious)
    start_time = time.time()
    uname, pword = gen_creds() # generates credentials (pass, user)
    
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new") # makes browser not visible
    
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
    chrome_options.add_argument("--window-size=1280,720")

    service = Service(executable_path='chromedriver.exe') # get chromedriver.exe (included in .zip)
    browser = webdriver.Chrome(service=service, options=chrome_options)

    try:
        print(f"{Fore.CYAN}[*] starting: {uname}") # start gen
        browser.get('https://www.roblox.com')
        wait = WebDriverWait(browser, 15)

        # step 1: accept cookies
        try:
            cookie_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "cookie-btn")))
            browser.execute_script("arguments[0].click();", cookie_btn)
        except: pass

        # step 2: birthday
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        Select(wait.until(EC.presence_of_element_located((By.ID, "MonthDropdown")))).select_by_value(random.choice(months))
        Select(browser.find_element(By.ID, "DayDropdown")).select_by_index(random.randint(1, 28))
        Select(browser.find_element(By.ID, "YearDropdown")).select_by_index(random.randint(18, 30))

        # step 3: credentials
        browser.find_element(By.ID, "signup-username").send_keys(uname)
        browser.find_element(By.ID, "signup-password").send_keys(pword)
        
        gender_id = "MaleButton" if random.random() > 0.5 else "FemaleButton"
        browser.execute_script("arguments[0].click();", browser.find_element(By.ID, gender_id))
        
        # validation wait
        time.sleep(2)
        try:
            val_msg = browser.find_element(By.ID, "signup-usernameInputValidation")
            if val_msg.is_displayed():
                error_text = val_msg.text.strip()
                if "appropriate" in error_text.lower() or "use" in error_text.lower():
                    print(f"{Fore.YELLOW}[-] skipped: {uname} ({error_text})")
                    send_webhook(uname, False, time.time()-start_time, error_text)
                    return 
        except: pass

        # click sign up
        browser.execute_script("arguments[0].click();", browser.find_element(By.ID, "signup-button"))
        
        # step 4: success/fail loop
        success = False
        reason = "timeout"
        
        for i in range(25):
            current_url = browser.current_url
            
            # priority 1: check success
            if "roblox.com/home" in current_url or "roblox.com/games" in current_url:
                success = True
                break
            
            # priority 2: check for general error (ip ratelimit / site issue)
            try:
                gen_err = browser.find_element(By.ID, "GeneralErrorText")
                if gen_err.is_displayed():
                    reason = "site/ip blocked fuck you roblox!" # ud real +rep
                    break 
            except: pass

            # priority 3: check for captchas! (i hate captchas)
            if "arkose" in browser.page_source.lower():
                reason = "blocked by captcha"
            
            time.sleep(1)
        
        elapsed = time.time() - start_time
        if success:
            print(f"{Fore.GREEN}[+] success: {uname} ({elapsed:.2f}s)")
            with file_lock:
                with open(output, "a") as f:
                    f.write(f"{uname}:{pword}\n")
            send_webhook(uname, True, elapsed)
        else:
            print(f"{Fore.RED}[-] failed: {uname} - {reason}")
            send_webhook(uname, False, elapsed, reason)

    except Exception as e:
        print(f"{Fore.RED}[!] error: {str(e)[:60]}")
    finally:
        browser.quit()

if __name__ == "__main__": # main
    print(f"{Fore.MAGENTA}{Style.BRIGHT}[*] STARTING 67 MANGO GEN SO TUFF BOII 6777 TUNG TUNG TUNG SAHUR") # +rep
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        for _ in range(attempts):
            executor.submit(create_account) # make account boom ez you get accounts 
            time.sleep(2)
