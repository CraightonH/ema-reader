from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import config
import secret
from time import sleep

def setupDriver():
    options = Options()
    for opt in config.driver_opts: 
        options.add_argument(opt)
    return webdriver.Firefox(options=options)

def logout(driver):
    top_menu = driver.find_element(By.CLASS_NAME, "div_menu2")
    anchors = top_menu.find_elements(By.TAG_NAME, "a")
    sign_out = anchors[len(anchors) - 1]
    assert sign_out.text == config.sign_out_text
    sign_out.click()
    print(driver.current_url)
    driver.close()

def login(driver):
    try:
        driver.get(config.login_url)
        # print("current url: " + driver.current_url)

        input_username = driver.find_element(By.ID, config.username_element_id)
        input_username.clear()
        input_username.send_keys(secret.username)
        # print("input.username: " + input_username.get_attribute("value"))

        input_password = driver.find_element(By.ID, config.password_element_id)
        input_password.clear()
        input_password.send_keys(secret.password)
        # print("input.password: " + input_password.get_attribute("value"))

        assert input_username.get_attribute("value") == secret.username and input_password.get_attribute("value") == secret.password

        driver.find_element(By.ID, config.login_button_element_id).click()

        assert config.exception_page not in driver.current_url

        return True
    except:
        print("Username field not found.")
        return False

def getProductionInfo(driver):
    return False

if __name__ == "__main__":
    driver = setupDriver()
    print("Logging in to " + config.login_url)
    if login(driver):
        # print("cookies: " + driver.get_cookies)
        print("Successfully logged in")
        getProductionInfo(driver)
        sleep(2)
        logout(driver)
    else:
        print("ERROR: Unable to login")
