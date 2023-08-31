import time

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
from fake_useragent import UserAgent
import datetime

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import Accounts.models
from django.conf import settings
from django.conf import settings
ua = UserAgent()
user_agent = ua.ff
options = webdriver.ChromeOptions()
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-extensions")
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--proxy-server='direct://'")
options.add_argument("--proxy-bypass-list=*")

if settings.SERV:
    options.add_argument("--headless")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("-disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
selpath = "/home/vanua/PycharmProjects/django/VolunteerE-book/chromedriver"
if settings.SERV:
    selpath = "/root/Ebook1/Accounts/chromedriver"

def get_token(user_login, user_password):
    start = datetime.datetime.now()
    driver = webdriver.Chrome(options=options,
                              service=Service(
                                  executable_path=selpath))
    driver.get(
        "https://login.mos.ru/sps/login/methods/password?bo=%2Fsps%2Foauth%2Fae%3Fresponse_type%3Dcode%26access_type"
        "%3Doffline%26client_id%3Ddnevnik.mos.ru%26scope%3Dopenid%2Bprofile%2Bbirthday%2Bcontacts%2Bsnils"
        "%2Bblitz_user_rights%2Bblitz_change_password%26redirect_uri%3Dhttps%253A%252F%252Fschool.mos.ru%252Fv3%252Fauth"
        "%252Fsudir%252Fcallback")


    WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.NAME, 'login')))
    #time.sleep(10)
    login = driver.find_element(By.NAME, "login")
    password = driver.find_element(By.NAME, "password")
    button = driver.find_element(By.ID, "bind")
    login.click()
    login.send_keys(user_login)
    password.click()
    password.send_keys(user_password)
    button.click()
    state = True
    timer = 10
    while state:
        if timer == 0:
            break
        if driver.current_url == "https://school.mos.ru/auth/callback":
            state = False
            print(datetime.datetime.now() - start)

        timer -= 1
        time.sleep(1)
    if not state:
        token = driver.get_cookie("aupd_token")
        if token:
            token = token['value']
        else:
            token = False
        driver.get(
            "https://login.mos.ru/sps/login/logout?post_logout_redirect_uri=https://www.mos.ru/api/acs/v1/logout"
            "/satisfy")
        return token
    else:
        return False
