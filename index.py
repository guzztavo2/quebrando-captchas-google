from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from capmonster_python import RecaptchaV2EnterpriseTask

API_KEY_CAPMONSTER = ""
url_to_get = ""
def goToUrl(driver):
    global url_to_get
    driver.get(url_to_get)

def resolver_captcha_capmonster(driver, max_attempts=3):
    attempts = 0
    global API_KEY_CAPMONSTER

    while attempts < max_attempts:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="g-recaptcha-response"]'))
            )

            solver = RecaptchaV2EnterpriseTask(API_KEY_CAPMONSTER)

            grecaptcha_cfg = driver.execute_script("return typeof ___grecaptcha_cfg !== 'undefined'")
            if not grecaptcha_cfg:
                print("Dont find ___grecaptcha_cfg.")
                return
            
            siteApiKey = driver.execute_script(""" 
                for(const object of Object.values(___grecaptcha_cfg.clients[0])){
                    if(!object || typeof object != 'object')
                        continue;
                    const elements = Object.values(object);
                    if(elements.length == 0 || elements == undefined)
                        continue;
                    for(const element of elements){
                        if(element == null || typeof element != 'object')
                        continue;
                        if(Object.keys(element).includes('sitekey')){
                            return (element['sitekey']);
                        }
                    }
                }
            """)
            siteUrl = driver.current_url
            
            task_id = solver.create_task(siteUrl, siteApiKey)
            result = solver.join_task_result(task_id)

            driver.execute_script(""" 
                for(const object of Object.values(___grecaptcha_cfg.clients[0])){
                    if(!object || typeof object != 'object')
                    continue;
                    const elements = Object.values(object);
                    if(elements.length == 0 || elements == undefined)
                        continue;
                    for(const element of elements){
                        if(element == null || typeof element != 'object')
                        continue;
                        if(Object.keys(element).includes('sitekey')){
                            element['callback']('""" + result.get('text') + """');
                        }
                    }
                }
            """)
            return "OK"
        
        except Exception as e:
            attempts += 1
            print(f"Error solving CAPTCHA with CapMonster (Attempt {attempts}): {str(e)}")
            if attempts < max_attempts:
                time.sleep(2)
            else:
                print("Maximum number of attempts reached. Could not solve the CAPTCHA.")
                return
 
def initScreen():
    options = webdriver.ChromeOptions()
    options.add_argument("-disable-quic")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-infobars")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument(f'user-agent=Mozilla/5.0')

    driver = webdriver.Chrome(options=options)
    goToUrl(driver)
    
    driver.implicitly_wait(30)
    
    resolver_captcha_capmonster(driver)
    driver.quit()

 
initScreen()
