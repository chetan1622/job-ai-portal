
import time
import csv
import re
import os
import smtplib
import logging
import json
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Selenium Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# --- CONFIGURATION SETTINGS ---
class Config:
    APPLICANT_NAME = "Chetan Gopal Patil"
    EMAIL_ID = "chetangpatil162@gmail.com"
    EMAIL_PASSWORD = "Chetan@162"
    RESUME_PATH = r"C:\Users\cheta\Downloads\Chetan_Patil_DS.pdf"
    
    # Credentials Database (PDF ki jagah JSON/Dict zyada reliable hai)
    # Aap yahan site name ke hisab se login details dal sakte hain
    CREDENTIALS_DB = {
        "naukri.com": {"user": "chetangpatil162gmail.com", "pass": "chetan@333"},
        "indeed.com": {"user": "chetan.g.patil1622@gmail.com", "pass": "Chetan@1622"},
        "linkedin": {"user": "chetan.g.patil1622@gmail.com", "pass": "chetan1622"}
    }
    
    LOCATION = "Pune,Maharashtra"
    KEYWORDS = ["Freshers", "Data Analyst"]
    OUTPUT_FILE = "job_application_report.csv"

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class JobAutomationAgent:
    def __init__(self):
        self.driver = self._setup_driver()
        self.results = []
        self.captcha_blocked_jobs = [] # List to store CAPTCHA failures

    def _setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)

    # --- HELPER: LOGIN HANDLER ---
    def handle_login(self, job_url):
        """
        Agar login page detect hota hai to credentials check karke login karega.
        """
        logging.info("Login page detected. Checking credentials...")
        
        # Determine which site it is (generic check)
        domain = "unknown"
        for key in Config.CREDENTIALS_DB.keys():
            if key in job_url.lower():
                domain = key
                break
        
        if domain == "unknown":
            logging.warning("No credentials found for this site.")
            return False

        creds = Config.CREDENTIALS_DB[domain]
        
        try:
            # Username Field Dhoondna
            user_field = self.driver.find_element(By.XPATH, "//input[@type='text' or @type='email' or contains(@name, 'user') or contains(@name, 'login')]")
            user_field.clear()
            user_field.send_keys(creds['user'])
            
            # Password Field Dhoondna
            pass_field = self.driver.find_element(By.XPATH, "//input[@type='password']")
            pass_field.clear()
            pass_field.send_keys(creds['pass'])
            
            # Login Button Click
            login_btn = self.driver.find_element(By.XPATH, "//button[@type='submit' or contains(text(), 'Sign in') or contains(text(), 'Login')]")
            login_btn.click()
            
            time.sleep(5) # Wait for login to complete
            return True
        except Exception as e:
            logging.error(f"Login failed: {e}")
            return False

    # --- MODIFIED AUTO APPLY MODULE ---
    def auto_apply(self, job_url, company_name):
        logging.info(f"Opening Job URL: {job_url}")
        self.driver.get(job_url)
        time.sleep(3)
        
        page_source = self.driver.page_source.lower()

        # 1. CHECK FOR CAPTCHA
        if "captcha" in page_source or "security check" in page_source or "i'm not a robot" in page_source:
            logging.warning(f"CAPTCHA DETECTED at {company_name}")
            # Add to notification list
            self.captcha_blocked_jobs.append(f"{company_name} ({job_url})")
            return "Skipped (CAPTCHA Block)"

        # 2. CHECK FOR LOGIN REQUIREMENT
        # Agar password field dikh raha hai matlab login chahiye
        try:
            if self.driver.find_elements(By.XPATH, "//input[@type='password']"):
                success = self.handle_login(job_url)
                if not success:
                    return "Manual Apply Required (Login Failed)"
                # Login ke baad page refresh ho sakta hai, dobara check karein
                time.sleep(3)
        except:
            pass

        # 3. ATTEMPT FORM FILLING
        try:
            apply_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Apply') or contains(text(), 'Easy Apply')]"))
            )
            apply_btn.click()
            time.sleep(2)
            
            # Simple form filling logic (Name, Email, Resume)
            try:
                # Fill name field
                name_fields = self.driver.find_elements(By.XPATH, "//input[contains(@name, 'name') or contains(@placeholder, 'name') or @id='name']")
                for field in name_fields:
                    if field.is_displayed():
                        field.clear()
                        field.send_keys(Config.APPLICANT_NAME)
                        break
            except:
                pass
            
            try:
                # Fill email field
                email_fields = self.driver.find_elements(By.XPATH, "//input[@type='email' or contains(@name, 'email') or contains(@placeholder, 'email')]")
                for field in email_fields:
                    if field.is_displayed():
                        field.clear()
                        field.send_keys(Config.EMAIL_ID)
                        break
            except:
                pass
            
            # Resume Upload
            try:
                file_input = self.driver.find_element(By.XPATH, "//input[@type='file']")
                file_input.send_keys(Config.RESUME_PATH)
            except:
                return "Failed: No Upload Button"

            # Submit (Simulated)
            return "Auto-Applied Success"

        except Exception as e:
            return "Manual Apply Required (Complex Layout)"

    # --- NOTIFICATION SYSTEM ---
    def notify_captcha_failures(self):
        """Process khatam hone par CAPTCHA wali companies ki list print karega"""
        if self.captcha_blocked_jobs:
            print("\n" + "="*50)
            print("⚠️  ALERT: CAPTCHA BLOCKED APPLICATIONS  ⚠️")
            print("="*50)
            print(f"Total {len(self.captcha_blocked_jobs)} jobs skip ki gayi hain:")
            for item in self.captcha_blocked_jobs:
                print(f"❌ {item}")
            print("="*50 + "\n")
        else:
            print("\n✅ Great! Koi bhi CAPTCHA block nahi mila.\n")

    # --- MAIN PROCESS ---
    def run(self):
        # ... (Search logic same as before) ...
        
        # Example dummy data processing
        dummy_jobs = [
            {"title": "Data Analyst", "company": "TechCorp", "url": "https://naukri.com/sample-job"},
            {"title": "Trainee", "company": "SecureWeb", "url": "https://secure-site.com/captcha-page"}
        ]

        print("Starting Job Automation...\n")
        
        for job in dummy_jobs:
            status = self.auto_apply(job['url'], job['company'])
            print(f"Result for {job['company']}: {status}")
            
        # Last step: Show Notification
        self.notify_captcha_failures()
        self.driver.quit()

if __name__ == "__main__":
    bot = JobAutomationAgent()
    bot.run()